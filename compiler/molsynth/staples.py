"""
Build the orderable staple set from a scaffold Routing.

Staples are the exact reverse complement of the scaffold route, broken into short
oligos (32-42 nt) by the yield optimizer. Because each staple is the true reverse
complement of a contiguous stretch of scaffold, it WILL hybridise to that stretch -
the sequences are chemically valid and directly orderable from IDT/Twist. Staples
whose scaffold span crosses a vertex boundary physically bridge two helices and act
as crossover staples that hold the wireframe together.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import sequences as sq
from .optimizer import YieldModel, anneal


@dataclass
class Staple:
    index: int
    name: str
    well: str
    seq: str
    length: int
    gc: float
    tm_C: float
    max_run: int
    repeats: int
    hairpin: int
    crossovers: int       # vertex/loop-closures this staple bridges (Aksel 2024: keep low)
    scaffold_start: int   # scaffold coordinate of the staple's 5' complement region
    scaffold_end: int
    offtarget: int = 0    # longest scaffold-repeat stretch inside this staple (off-target risk)
    # rung-2 functionalisation (empty unless --decorate); see decorate.py
    handle: str = ""      # single-stranded handle appended to one end (positions a guest)
    handle_end: str = ""  # "3p" or "5p"
    spacer: str = "TT"    # flexible spacer between binding region and handle
    guest: str = ""       # label of the guest this site carries

    @property
    def order_seq(self) -> str:
        """The full sequence to ORDER (binding region + spacer + handle). Equals the
        binding region `seq` when undecorated, so the scaffold-complementarity of `seq`
        is preserved (the handle is a non-binding overhang)."""
        if not self.handle:
            return self.seq
        if self.handle_end == "5p":
            return self.handle + self.spacer + self.seq
        return self.seq + self.spacer + self.handle


def _well(i: int) -> str:
    """96-well plate position, column-major A1..H12 then plate 2, ..."""
    plate = i // 96
    within = i % 96
    row = "ABCDEFGH"[within % 8]
    col = within // 8 + 1
    tag = f"{row}{col}"
    return tag if plate == 0 else f"P{plate + 1}-{tag}"


def build_staples(routing, model: YieldModel | None = None,
                  iterations=4000, seed=12345, design_name="design",
                  offtarget_mask=None):
    """Return (list[Staple], optimizer_history)."""
    model = model or YieldModel()
    template = sq.reverse_complement(routing.scaffold_seq)
    S = len(template)

    cuts, seqs, counts, history = anneal(
        template, routing.crossover_positions, model,
        iterations=iterations, seed=seed, offtarget_mask=offtarget_mask,
    )

    staples = []
    # walk spans in template coordinates; map back to scaffold coordinates
    prev = 0
    spans = []
    for c in cuts + [S]:
        spans.append((prev, c))
        prev = c
    for i, ((a, b), seq, cross) in enumerate(zip(spans, seqs, counts)):
        # template[a:b] reverse-complements scaffold[S-b : S-a]
        sc_start, sc_end = S - b, S - a
        # report Tm at the real ~12.5 mM Mg2+ folding-buffer salt ([Na+]_eq=0.166; exp1),
        # the same scale the optimizer scores against -> staples.csv / diagnostics histogram /
        # the optimizer Tm window are all consistent (not the 50 mM under-prediction).
        info = sq.describe(seq, na_M=0.166)
        staples.append(Staple(
            index=i,
            name=f"{design_name}-st{i:03d}",
            well=_well(i),
            seq=seq,
            length=info["length"],
            gc=info["gc"],
            tm_C=info["tm_C"],
            max_run=info["max_run"],
            repeats=info["repeats"],
            hairpin=info["hairpin"],
            crossovers=int(cross),
            scaffold_start=sc_start,
            scaffold_end=sc_end,
            offtarget=(sq.longest_run(offtarget_mask, sc_start, sc_end)
                       if offtarget_mask is not None else 0),
        ))
    return staples, history


def cross_dimer_screen(staples, k=8):
    """Flag staples that are complementary to EACH OTHER (form dimers, lowering yield).
    Index forward k-mers, then for each staple look up its reverse-complement k-mers
    (efficient); compute the exact longest complement for flagged pairs. Returns the
    worst dimer length, the offending pair, and the count of dimer-prone pairs (>=k)."""
    index = {}
    for i, st in enumerate(staples):
        s = st.seq
        for p in range(len(s) - k + 1):
            index.setdefault(s[p:p + k], set()).add(i)
    pairs = set()
    for i, st in enumerate(staples):
        rc = sq.reverse_complement(st.seq)
        for p in range(len(rc) - k + 1):
            for j in index.get(rc[p:p + k], ()):
                if j != i:
                    pairs.add((min(i, j), max(i, j)))
    worst, worst_pair = 0, None
    for i, j in pairs:
        d = sq.cross_dimer_len(staples[i].seq, staples[j].seq)
        if d > worst:
            worst, worst_pair = d, (staples[i].name, staples[j].name)
    return {"max_cross_dimer": worst, "n_dimer_pairs": len(pairs),
            "worst_pair": list(worst_pair) if worst_pair else None}


def staple_stats(staples):
    if not staples:
        return {}
    tms = [s.tm_C for s in staples]
    lens = [s.length for s in staples]
    mean = sum(tms) / len(tms)
    var = sum((t - mean) ** 2 for t in tms) / len(tms)
    return {
        "n_staples": len(staples),
        "n_crossover_staples": sum(1 for s in staples if s.crossovers > 0),
        "n_overloaded_staples": sum(1 for s in staples if s.crossovers > 2),
        "len_min": min(lens),
        "len_max": max(lens),
        "len_mean": round(sum(lens) / len(lens), 1),
        "tm_min_C": round(min(tms), 1),
        "tm_max_C": round(max(tms), 1),
        "tm_mean_C": round(mean, 1),
        "tm_stdev_C": round(var ** 0.5, 2),
        "total_bases_ordered": sum(lens),
        "offtarget_max": max((s.offtarget for s in staples), default=0),
        "n_offtarget_risk": sum(1 for s in staples if s.offtarget > 14),
        **{f"dimer_{kk}": vv for kk, vv in cross_dimer_screen(staples).items()},
    }
