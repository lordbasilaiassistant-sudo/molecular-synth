"""
Sequence thermodynamics for DNA staple design.

Implements the unified nearest-neighbor (NN) model of SantaLucia (1998) for
predicting duplex stability (delta-H, delta-S) and melting temperature (Tm),
plus the sequence-quality heuristics the optimizer uses as a yield proxy
(GC content, homopolymer runs, internal repeats, hairpin propensity).

Reference for the NN parameters and Tm equation:
  J. SantaLucia Jr., "A unified view of polymer, dumbbell, and oligonucleotide
  DNA nearest-neighbor thermodynamics," PNAS 95, 1460-1465 (1998).
  https://doi.org/10.1073/pnas.95.4.1460
Salt correction:
  Owczarzy et al., Biochemistry 43, 3537-3554 (2004).
  https://doi.org/10.1021/bi034621r

These are the textbook values used by IDT's OligoAnalyzer and primer3; balancing
staple Tm with this model is the standard route to cooperative, high-yield folding
(see docs/science.md, "AI / yield model").
"""

from __future__ import annotations

import math

# Gas constant, cal / (mol K)
R = 1.987

_COMPLEMENT = {"A": "T", "T": "A", "G": "C", "C": "G",
               "a": "t", "t": "a", "g": "c", "c": "g", "N": "N", "n": "n"}

# Unified NN parameters, 5'->3' top strand dinucleotide -> (dH kcal/mol, dS cal/mol/K)
# SantaLucia 1998, Table 1 (1 M NaCl reference state).
NN_PARAMS = {
    "AA": (-7.9, -22.2), "AC": (-8.4, -22.4), "AG": (-7.8, -21.0), "AT": (-7.2, -20.4),
    "CA": (-8.5, -22.7), "CC": (-8.0, -19.9), "CG": (-10.6, -27.2), "CT": (-7.8, -21.0),
    "GA": (-8.2, -22.2), "GC": (-9.8, -24.4), "GG": (-8.0, -19.9), "GT": (-8.4, -22.4),
    "TA": (-7.2, -21.3), "TC": (-8.2, -22.2), "TG": (-8.5, -22.7), "TT": (-7.9, -22.2),
}

# Initiation terms (SantaLucia 1998): applied per duplex end by the identity of the
# terminal base pair.
INIT_GC = (0.1, -2.8)    # (dH, dS) for a terminal G.C pair
INIT_AT = (2.3, 4.1)     # (dH, dS) for a terminal A.T pair


def complement(seq: str) -> str:
    return "".join(_COMPLEMENT.get(b, "N") for b in seq)


def reverse_complement(seq: str) -> str:
    return "".join(_COMPLEMENT.get(b, "N") for b in reversed(seq))


def gc_content(seq: str) -> float:
    seq = seq.upper()
    if not seq:
        return 0.0
    return (seq.count("G") + seq.count("C")) / len(seq)


def nn_thermo(seq: str):
    """Return (delta_H kcal/mol, delta_S cal/mol/K) for a perfectly matched duplex
    of the given top-strand sequence under the SantaLucia 1998 unified model."""
    seq = seq.upper()
    if len(seq) < 2:
        return 0.0, 0.0
    dH = 0.0
    dS = 0.0
    for i in range(len(seq) - 1):
        pair = seq[i:i + 2]
        h, s = NN_PARAMS.get(pair, (0.0, 0.0))
        dH += h
        dS += s
    # initiation at each end, keyed on the terminal base
    for end in (seq[0], seq[-1]):
        h, s = INIT_GC if end in "GC" else INIT_AT
        dH += h
        dS += s
    return dH, dS


def tm(seq: str, strand_conc_M: float = 0.25e-6, na_M: float = 0.05) -> float:
    """Predicted melting temperature in degrees Celsius.

    strand_conc_M : total oligo strand concentration (staples are non-self-
                    complementary, so the x=4 factor is used).
    na_M          : monovalent-cation-equivalent concentration. For Mg2+ folding
                    buffer (~12.5 mM MgCl2), a common rule of thumb is
                    [Na+]_eq ~ 120 * sqrt([Mg2+]) ; the default 0.05 M approximates
                    a TAE/Mg origami buffer. Adjust for exact predictions.

    Assumes a NON-self-complementary strand (the C_T/4 factor; no symmetry term) -
    valid for origami staples, but not for self-complementary oligos.
    """
    seq = seq.upper().replace(" ", "")
    if len(seq) < 2:
        return float("nan")
    dH, dS = nn_thermo(seq)
    # 1 M NaCl reference Tm
    tm_1m = (dH * 1000.0) / (dS + R * math.log(strand_conc_M / 4.0))
    # Owczarzy 2004 salt correction (monovalent), applied to 1/Tm
    f_gc = gc_content(seq)
    ln_na = math.log(max(na_M, 1e-6))
    inv_tm = (1.0 / tm_1m) + (4.29 * f_gc - 3.95) * 1e-5 * ln_na + 9.40e-6 * ln_na ** 2
    return (1.0 / inv_tm) - 273.15


def max_homopolymer_run(seq: str) -> int:
    """Length of the longest run of a single base (poly-A/T/G/C). Long runs hurt
    synthesis fidelity and folding."""
    seq = seq.upper()
    best = run = 0
    prev = ""
    for b in seq:
        run = run + 1 if b == prev else 1
        prev = b
        best = max(best, run)
    return best


def repeat_penalty(seq: str, k: int = 6) -> int:
    """Count of internal k-mers that occur more than once. Repeated subsequences
    promote off-target / mis-paired staple binding."""
    seq = seq.upper()
    if len(seq) < k:
        return 0
    seen = {}
    extra = 0
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i + k]
        seen[kmer] = seen.get(kmer, 0) + 1
        if seen[kmer] > 1:
            extra += 1
    return extra


def hairpin_score(seq: str, stem: int = 5, min_loop: int = 3) -> int:
    """Cheap self-complementarity / hairpin proxy: number of positions where a
    `stem`-length window is reverse-complementary to a downstream window
    (separated by at least `min_loop`). A real design would call ViennaRNA/NUPACK;
    this keeps the compiler dependency-free for the end-to-end path."""
    seq = seq.upper()
    n = len(seq)
    hits = 0
    for i in range(n - stem + 1):
        window = seq[i:i + stem]
        rc = reverse_complement(window)
        j = seq.find(rc, i + stem + min_loop)
        if j != -1:
            hits += 1
    return hits


def repeat_mask(seq: str, k: int = 10) -> list:
    """Mark every position covered by a k-mer that occurs MORE THAN ONCE in `seq`.

    The M13mp18 scaffold contains >100 repeats >=8 nt (Nguyen et al.); a staple whose
    binding region overlaps a long duplicated stretch can bind that stretch's OTHER
    copy (off-target), lowering yield. This mask lets the compiler measure and the
    optimizer avoid putting a long scaffold-repeat inside a single staple."""
    seq = seq.upper()
    n = len(seq)
    mask = [False] * n
    if n < k:
        return mask
    counts = {}
    for i in range(n - k + 1):
        kmer = seq[i:i + k]
        counts[kmer] = counts.get(kmer, 0) + 1
    for i in range(n - k + 1):
        if counts[seq[i:i + k]] > 1:
            for j in range(i, i + k):
                mask[j] = True
    return mask


def lcs_len(a: str, b: str) -> int:
    """Longest common substring length of a and b (DP)."""
    if not a or not b:
        return 0
    nb = len(b)
    prev = [0] * (nb + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (nb + 1)
        ai = a[i - 1]
        row = b
        for j in range(1, nb + 1):
            if ai == row[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def cross_dimer_len(a: str, b: str) -> int:
    """Longest stretch over which staple a is complementary to staple b (they would
    hybridise to EACH OTHER = a dimer, instead of binding the scaffold)."""
    return lcs_len(reverse_complement(a), b)


def longest_run(mask: list, a: int, b: int) -> int:
    """Longest run of True in mask[a:b] (the off-target stretch length of a staple)."""
    best = run = 0
    for i in range(max(0, a), min(b, len(mask))):
        run = run + 1 if mask[i] else 0
        if run > best:
            best = run
    return best


def describe(seq: str, **tm_kwargs) -> dict:
    """Full per-staple quality readout."""
    return {
        "length": len(seq),
        "gc": round(gc_content(seq), 3),
        "tm_C": round(tm(seq, **tm_kwargs), 2),
        "max_run": max_homopolymer_run(seq),
        "repeats": repeat_penalty(seq),
        "hairpin": hairpin_score(seq),
    }
