"""
The "AI / yield" layer: choose staple break points to maximise predicted folding
yield.

Grounded in the best experimentally-validated result in the field:
  Aksel, T. et al. (Douglas lab), "Design principles for accurate folding of DNA
  origami," PNAS 121(48):e2406769121 (2024). https://doi.org/10.1073/pnas.2406769121
  (code: github.com/douglaslab/pyOrigamiBreak). Their finding — which most CAD tools
  ignore — is that yield is governed by the BALANCE between a staple's hybridization
  (binding) and its scaffold loop-closures: each loop closure pays an entropic penalty,
  so naively maximising binding length can hurt. Optimising that balance gave large,
  design-specific accuracy/yield gains (e.g. ~2%->61% on a test block) by gel + TEM.

So the objective is NOT "reward crossovers" (a naive mistake) and NOT "minimise
crossovers" either (that would nick the structure) -- it is a BALANCE:
  (a) every vertex/crossover boundary must be BRIDGED by exactly one staple (else the
      wireframe is nicked there), AND
  (b) no single staple should bridge more than ~xmax (=2) boundaries (loop entropy),
plus the classic terms: per-staple melting temperature clustered in a window
(SantaLucia NN model; sequences.py) for cooperative annealing, minimal repeated
k-mers, no long homopolymer runs, no strong hairpins.

`YieldModel` turns those into one score. The weights ARE the model parameters: the
default is an interpretable, literature-weighted heuristic, but `YieldModel.load()`
reads learned weights from JSON, so a model trained on real gel/TEM yield data drops
in without touching the optimizer. `anneal()` does simulated annealing over the cut
positions (the flexible backend from Babatunde 2021; a k-shortest-path backend is the
deterministic alternative used by pyOrigamiBreak), then `equalize_tm()` runs a focused
deterministic pass that tightens the per-staple Tm SPREAD (cooperative annealing) while
preserving the hard guarantees -- length window, crossover coverage, loop balance,
off-target. Crucially, anneal() keeps that refinement ONLY when it lowers the FULL
objective: Tm variance is already a scored term (w_tm_var), and an experiment showed that
accepting it on Tm-stdev alone net-WORSENED predicted yield on every small preset (it
overshot variance and paid more in the Tm-window penalty). So it now acts as a deterministic
refiner that can never worsen what the SA found, and still helps on the large presets.

Honest framing: this is a physics-grounded optimizer with an ML-ready scoring hook,
not a black-box neural net. That is the defensible, demonstrated claim and the
project's revenue surface. See docs/research/06-ai-staple-optimizer.md.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field

from . import sequences as sq

DEFAULT_WEIGHTS = {
    "len_lo": 32, "len_hi": 42,
    # Tm window in the REAL folding buffer (~12.5 mM Mg2+). The model scores every Tm at the
    # buffer-accurate salt (tm_kwargs na_M=0.166; research/exp1), so the window must be on that
    # same scale. The old [50,64] was a 50-mM-Na window; the buffer fold runs ~+9 C hotter
    # (exp1, measured +9.0 C mean on the octahedron), so the physically-equivalent window is
    # [59,73]. Window and salt shift together -> the dominant Tm-window term (exp3) now targets
    # the temperature staples actually melt at, instead of fighting a mis-calibrated target.
    "tm_lo": 59.0, "tm_hi": 73.0,
    "xmax": 2,            # crossovers/loop-closures per staple before penalty (Aksel 2024)
    "w_len": 1.0,        # penalty per nt outside the length window
    "w_tm": 0.5,         # penalty per degC outside the Tm window
    "w_tm_var": 2.0,     # penalty on the spread (stdev) of Tm across staples
    "w_repeat": 0.4,     # penalty per repeated k-mer
    "w_run": 1.0,        # penalty per nt of homopolymer run beyond 4
    "w_hairpin": 0.8,    # penalty per hairpin hit
    "w_loop": 1.5,       # penalty per crossover beyond xmax (loop-closure entropy) -- weight high
    "w_loop_entropy": 0.2,  # penalty per ln(bases) enclosed in each loop (Jacobson-Stockmayer proxy)
    "w_uncovered": 3.0,  # penalty per vertex boundary NOT bridged by any staple (structural nick)
    "w_offtarget": 0.6,  # penalty per nt of scaffold-repeat beyond offtarget_allow inside a staple
    "offtarget_allow": 14,  # contiguous scaffold-repeat length tolerated within one staple
    "w_dimer": 0.5,      # penalty per nt of worst staple-staple cross-dimer beyond dimer_allow
    "dimer_allow": 10,   # staple-staple complementary length tolerated (used in offset ranking)
    # --- kinetic folding-ORDER term (OPTIONAL; default OFF so behaviour is byte-identical) ---
    "w_kinetic": 0.0,    # reward a Tm gradient where high-load staples are NOT the hottest
    "kinetic_loop_w": 0.5,  # weight of ln(max enclosed loop) inside a staple's "load"
}


@dataclass
class YieldModel:
    weights: dict = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    # Score every Tm at the buffer-accurate monovalent equivalent of the 12.5 mM Mg2+ fold
    # ([Na+]_eq ~= 0.166 M; sequences.tm_buffer / research/exp1). sq.tm()'s 50 mM default
    # under-predicts the fold by ~9 C; scoring at the real salt makes the Tm window above mean
    # what it says. staples.py reports tm_C at this same salt, so the diagnostics histogram and
    # the window are on one consistent scale.
    tm_kwargs: dict = field(default_factory=lambda: {"na_M": 0.166})

    @classmethod
    def load(cls, path):
        """Load learned/overridden weights from JSON (ML-ready hook)."""
        with open(path, "r", encoding="utf-8") as fh:
            w = json.load(fh)
        merged = dict(DEFAULT_WEIGHTS)
        merged.update(w)
        return cls(weights=merged)

    def staple_seq_penalty(self, seq):
        """Per-staple sequence-quality penalty (no crossover term)."""
        w = self.weights
        n = len(seq)
        pen = 0.0
        if n < w["len_lo"]:
            pen += w["w_len"] * (w["len_lo"] - n)
        elif n > w["len_hi"]:
            pen += w["w_len"] * (n - w["len_hi"])
        t = sq.tm(seq, **self.tm_kwargs)
        if not math.isnan(t):
            if t < w["tm_lo"]:
                pen += w["w_tm"] * (w["tm_lo"] - t)
            elif t > w["tm_hi"]:
                pen += w["w_tm"] * (t - w["tm_hi"])
        pen += w["w_repeat"] * sq.repeat_penalty(seq)
        pen += w["w_run"] * max(0, sq.max_homopolymer_run(seq) - 4)
        pen += w["w_hairpin"] * sq.hairpin_score(seq)
        return pen

    def score_set(self, staple_seqs, cross_counts, loop_sizes, n_boundaries, n_covered,
                  offtarget_runs=None, staple_loop_loads=None):
        """Total objective for a full staple set (lower is better).

        staple_seqs    : list of staple sequences
        cross_counts   : crossovers (vertex boundaries) each staple bridges
        loop_sizes     : flat list of enclosed-loop sizes (bases) across all staples
        n_boundaries   : total vertex/crossover boundaries in the design
        n_covered      : how many of those boundaries are bridged by >=1 staple
        offtarget_runs : per-staple longest scaffold-repeat stretch (off-target risk)
        staple_loop_loads : OPTIONAL per-staple largest enclosed-loop size (bases). Only
                     used by the kinetic folding-ORDER term (w_kinetic); when None the loop
                     part of a staple's kinetic "load" is taken as 0 (crossover count only).
        """
        if not staple_seqs:
            return 1e9
        w = self.weights
        total = 0.0
        tms = []
        all_tms = []                                # parallel to staple_seqs (NaN kept)
        for idx, (seq, c) in enumerate(zip(staple_seqs, cross_counts)):
            total += self.staple_seq_penalty(seq)
            if c > w["xmax"]:                       # too many loop closures (Aksel 2024)
                total += w["w_loop"] * (c - w["xmax"])
            if offtarget_runs is not None and idx < len(offtarget_runs):
                total += w["w_offtarget"] * max(0, offtarget_runs[idx] - w["offtarget_allow"])
            t = sq.tm(seq, **self.tm_kwargs)
            all_tms.append(t)
            if not math.isnan(t):
                tms.append(t)
        for n in loop_sizes:
            if n > 1:
                total += w["w_loop_entropy"] * math.log(n)
        # structural integrity: every boundary must be bridged
        total += w["w_uncovered"] * max(0, n_boundaries - n_covered)
        # cooperative annealing: cluster every staple's Tm
        if len(tms) > 1:
            mean = sum(tms) / len(tms)
            var = sum((t - mean) ** 2 for t in tms) / len(tms)
            total += w["w_tm_var"] * math.sqrt(var)
        # kinetic folding-ORDER term (OPTIONAL; w_kinetic defaults to 0 -> no-op, byte-identical)
        if w.get("w_kinetic", 0.0):
            total += w["w_kinetic"] * kinetic_penalty(
                cross_counts, all_tms,
                loop_loads=staple_loop_loads,
                loop_w=w.get("kinetic_loop_w", 0.5))
        return total


def kinetic_penalty(cross_counts, tms, loop_loads=None, loop_w=0.5):
    """KINETIC folding-ORDER proxy (OPTIONAL term; see score_set's w_kinetic).

    The default objective is purely THERMODYNAMIC -- it clusters equilibrium melting
    temperatures so the staples cross their transition together (cooperative annealing,
    Aksel 2024). But real folding is a KINETIC, ordered process: as the pot is ramped
    down, staples bind in descending-Tm order, so the highest-Tm staples nucleate first.
    Two independent lines of work show that the ORDER matters as much as the endpoints:
    Sobczak et al., Science 338:1458 (2012) fold origami isothermally and find sharp,
    sequence-of-events-dependent optimal temperatures; Dunn et al., Nature 525:82 (2015)
    measure the folding pathway base-by-base and show that which staples engage first
    selects the final yield -- a hot loop-closing/seam staple that engages before its
    framework is laid down can lock in a kinetic trap.

    Defensible heuristic: a staple's "load" = (# crossovers it bridges) + loop_w * ln(max
    enclosed loop, in bases). High-load staples (multi-crossover bridges, large enclosed
    loops -- the structure's seams) should fold LATE, i.e. sit LOW in the Tm distribution,
    so the framework nucleates first. We penalise the positive covariance between load and
    Tm: reward designs where high-load staples are cooler, penalise designs where they are
    the hottest. Concretely, with mean-centred load L_i and mean-centred Tm T_i,

        penalty = max(0, sum_i L_i * T_i) / n        (only the WRONG-sign covariance costs).

    Zero when there is no load or no Tm spread, and zero when high-load staples are already
    the COOLEST (negative covariance is the desired gradient and is never rewarded below 0,
    only un-penalised). Units: degC * load, so w_kinetic is "penalty per degC*load of
    framework-before-seam inversion." This is a KINETIC PROXY built from the equilibrium Tm
    ranking -- there is NO molecular-dynamics kinetic simulator here; it encodes the
    descending-Tm folding-order assumption of the cited isothermal/pathway experiments.
    """
    n = len(cross_counts)
    if n < 2:
        return 0.0
    loads = []
    for i in range(n):
        load = float(cross_counts[i])
        if loop_loads is not None and i < len(loop_loads) and loop_loads[i] and loop_loads[i] > 1:
            load += loop_w * math.log(loop_loads[i])
        loads.append(load)
    pairs = [(loads[i], tms[i]) for i in range(n) if not math.isnan(tms[i])]
    if len(pairs) < 2:
        return 0.0
    lvals = [p[0] for p in pairs]
    tvals = [p[1] for p in pairs]
    lmean = sum(lvals) / len(lvals)
    tmean = sum(tvals) / len(tvals)
    cov = sum((l - lmean) * (t - tmean) for l, t in pairs) / len(pairs)
    return max(0.0, cov)


def boundaries_in(start, end, xovers):
    """Vertex boundaries strictly inside the half-open interval [start, end)."""
    return [c for c in xovers if start < c < end]


def max_cross_dimer(seqs, k=8):
    """Worst staple-staple cross-dimer (complementary stretch) across a set of staple
    sequences. Same k-mer-indexed shortlist as staples.cross_dimer_screen, but operates
    on raw strings so the scaffold-offset search can rank windows by dimer load before
    any Staple objects exist. Returns the longest complementary run found (0 if none)."""
    index = {}
    for i, s in enumerate(seqs):
        for p in range(len(s) - k + 1):
            index.setdefault(s[p:p + k], set()).add(i)
    pairs = set()
    for i, s in enumerate(seqs):
        rc = sq.reverse_complement(s)
        for p in range(len(rc) - k + 1):
            for j in index.get(rc[p:p + k], ()):
                if j != i:
                    pairs.add((i, j) if i < j else (j, i))
    worst = 0
    for i, j in pairs:
        d = sq.cross_dimer_len(seqs[i], seqs[j])
        if d > worst:
            worst = d
    return worst


def proxy_score(routing, model: YieldModel, offtarget_mask=None, target_len=37):
    """Cheap quality estimate of a routing WITHOUT running SA: the objective of a single
    EVEN partition. The offset's intrinsic quality (its M13 region's Tm distribution and
    repeat content) is mostly captured by the even partition, so this ranks scaffold
    offsets ~as well as a full anneal at a tiny fraction of the cost."""
    template = sq.reverse_complement(routing.scaffold_seq)
    S = len(template)
    lo, hi = model.weights["len_lo"], model.weights["len_hi"]
    xovers_t = sorted(S - p for p in routing.crossover_positions if 0 < p < S)
    n_boundaries = len(xovers_t)
    if S <= hi:
        cuts = []
    else:
        n = max(1, round(S / target_len))
        n = max(n, math.ceil(S / hi))
        n = min(n, max(1, S // lo))
        cuts = sorted(set(round(S * k / n) for k in range(1, n)))
    spans, prev = [], 0
    for c in list(cuts) + [S]:
        spans.append((prev, c))
        prev = c
    seqs, counts, loops, offt, loop_loads = [], [], [], [], []
    covered = set()
    for a, b in spans:
        seqs.append(template[a:b])
        bnds = boundaries_in(a, b, xovers_t)
        counts.append(len(bnds))
        covered.update(bnds)
        pts = [a] + bnds + [b]
        seg_loops = [pts[i] - pts[i - 1] for i in range(1, len(pts))]
        loops.extend(seg_loops)
        loop_loads.append(max(seg_loops) if seg_loops else 0)
        if offtarget_mask is not None:
            offt.append(sq.longest_run(offtarget_mask, S - b, S - a))
    score = model.score_set(seqs, counts, loops, n_boundaries, len(covered),
                            offtarget_runs=offt if offtarget_mask is not None else None,
                            staple_loop_loads=loop_loads)
    # Make the offset search dimer-aware: penalise windows whose even-partition staples
    # are complementary to each other (form cross-dimers that compete with folding).
    w = model.weights
    if w.get("w_dimer", 0) and len(seqs) > 1:
        worst = max_cross_dimer(seqs)
        score += w["w_dimer"] * max(0, worst - w.get("dimer_allow", 10))
    return score


def equalize_tm(template, cuts, xovers_t, model, max_passes=6, offtarget_mask=None):
    """Deterministic post-SA refinement: nudge cut positions ONLY to reduce the spread
    (stdev) of staple melting temperatures, so the staples cross their folding transition
    together -- cooperative annealing, the lever for high origami yield (Aksel 2024). A
    move is accepted only if it lowers Tm stdev AND keeps both touched staples within
    [len_lo, len_hi] AND does not reduce crossover-boundary coverage (never a structural
    nick) AND does not increase loop-closure overload (preserves the Aksel 2024 balance).
    Because it protects every HARD guarantee, the caller keeps it whenever it tightens the
    spread. Hill-climbing with incremental Tm (only the two changed staples are recomputed),
    so it is cheap and can only tighten or hold the spread. Returns refined cuts."""
    w = model.weights
    lo, hi = w["len_lo"], w["len_hi"]
    xmax = w["xmax"]
    ot_allow = w["offtarget_allow"]
    S = len(template)
    cuts = sorted(cuts)
    if len(cuts) < 2:
        return cuts

    def ot_excess(a, b):
        """Off-target overload of the staple covering template [a,b) (scaffold [S-b,S-a))."""
        if offtarget_mask is None:
            return 0
        return max(0, sq.longest_run(offtarget_mask, S - b, S - a) - ot_allow)

    def bnds(cs):
        return [0] + list(cs) + [S]

    def stdev(ts):
        vals = [t for t in ts if not math.isnan(t)]
        if len(vals) < 2:
            return 0.0
        mu = sum(vals) / len(vals)
        return math.sqrt(sum((t - mu) ** 2 for t in vals) / len(vals))

    def coverage(cs):
        b = bnds(cs)
        cov = set()
        for i in range(len(b) - 1):
            cov.update(c for c in xovers_t if b[i] < c < b[i + 1])
        return len(cov)

    b0 = bnds(cuts)
    tl = [sq.tm(template[b0[i]:b0[i + 1]], **model.tm_kwargs) for i in range(len(b0) - 1)]
    base_cov = coverage(cuts)
    cur_sd = stdev(tl)
    for _ in range(max_passes):
        improved = False
        for k in range(len(cuts)):
            b = bnds(cuts)
            best = None
            for d in (-3, -2, -1, 1, 2, 3):
                nc = cuts[k] + d
                if not (b[k] < nc < b[k + 2]):          # stay strictly between neighbours
                    continue
                if not (lo <= nc - b[k] <= hi and lo <= b[k + 2] - nc <= hi):
                    continue
                trial = cuts[:k] + [nc] + cuts[k + 1:]
                if coverage(trial) < base_cov:
                    continue
                # preserve Aksel loop-balance: the two touched staples must not gain
                # crossover overload (excess beyond xmax) versus before the move.
                old_excess = (max(0, len(boundaries_in(b[k], b[k + 1], xovers_t)) - xmax)
                              + max(0, len(boundaries_in(b[k + 1], b[k + 2], xovers_t)) - xmax))
                new_excess = (max(0, len(boundaries_in(b[k], nc, xovers_t)) - xmax)
                              + max(0, len(boundaries_in(nc, b[k + 2], xovers_t)) - xmax))
                if new_excess > old_excess:
                    continue
                # also never increase off-target overload of the two touched staples
                if (ot_excess(b[k], nc) + ot_excess(nc, b[k + 2])
                        > ot_excess(b[k], b[k + 1]) + ot_excess(b[k + 1], b[k + 2])):
                    continue
                nt = list(tl)
                nt[k] = sq.tm(template[b[k]:nc], **model.tm_kwargs)
                nt[k + 1] = sq.tm(template[nc:b[k + 2]], **model.tm_kwargs)
                s = stdev(nt)
                if s < cur_sd - 1e-9 and (best is None or s < best[0]):
                    best = (s, trial, nt)
            if best:
                cuts, tl, cur_sd = best[1], best[2], best[0]
                improved = True
        if not improved:
            break
    return cuts


def anneal(template, crossover_positions_scaffold, model: YieldModel,
           iterations=4000, seed=12345, target_len=37, offtarget_mask=None):
    """Simulated annealing over the cut positions of the staple template.

    template : reverse complement of the scaffold route (the staple strand, 5'->3').
    crossover_positions_scaffold : vertex boundaries in SCAFFOLD coordinates.
    offtarget_mask : per-SCAFFOLD-position flag (route coords) for being inside a
                     scaffold repeat; staples spanning a long run are penalised so the
                     optimiser splits repeats across break points (reduces off-target).
    Returns (cuts, staple_seqs, cross_counts, score_history).
    """
    rng = random.Random(seed)
    S = len(template)
    lo, hi = model.weights["len_lo"], model.weights["len_hi"]

    # Map scaffold crossover positions into template coordinates.
    # template length == scaffold route length, so a boundary at scaffold pos p maps
    # to template index S - p (reverse-complement reversal).
    xovers_t = sorted(S - p for p in crossover_positions_scaffold if 0 < p < S)
    n_boundaries = len(xovers_t)

    # initial EVEN partition into n in-bounds staples (every piece within [lo,hi]).
    if S <= hi:
        cuts = []
    else:
        n = max(1, round(S / target_len))
        n = max(n, math.ceil(S / hi))       # enough pieces that none exceeds hi
        n = min(n, max(1, S // lo))         # not so many that pieces fall below lo
        cuts = sorted(set(round(S * k / n) for k in range(1, n)))

    def staple_spans(cs):
        spans = []
        prev = 0
        for c in list(cs) + [S]:
            spans.append((prev, c))
            prev = c
        return spans

    def evaluate(cs):
        spans = staple_spans(cs)
        seqs, counts, loops, offt, loop_loads = [], [], [], [], []
        covered = set()
        for a, b in spans:
            seqs.append(template[a:b])
            bnds = boundaries_in(a, b, xovers_t)
            counts.append(len(bnds))
            covered.update(bnds)
            pts = [a] + bnds + [b]
            seg_loops = [pts[i] - pts[i - 1] for i in range(1, len(pts))]
            loops.extend(seg_loops)
            loop_loads.append(max(seg_loops) if seg_loops else 0)
            if offtarget_mask is not None:
                # template span [a,b) <-> scaffold-route span [S-b, S-a)
                offt.append(sq.longest_run(offtarget_mask, S - b, S - a))
        score = model.score_set(seqs, counts, loops, n_boundaries, len(covered),
                                offtarget_runs=offt if offtarget_mask is not None else None,
                                staple_loop_loads=loop_loads)
        return score, seqs, counts

    def length_valid(cs):
        return all(lo <= (b - a) <= hi for a, b in staple_spans(cs))

    init_score, init_seqs, init_counts = evaluate(cuts)
    best_seqs, best_counts, best_cuts = init_seqs, init_counts, list(cuts)
    cur_score = init_score
    # Only accept a length-VALID partition as "best" (the SA-move guard below enforces
    # validity on every candidate). If the initial even partition is out of [lo,hi]
    # (only possible for pathologically short templates), seed best=inf so the first
    # valid SA state wins; the initial stays as a last-resort fallback.
    best_score = init_score if length_valid(cuts) else float("inf")
    history = [cur_score]

    for it in range(iterations):
        temp = max(0.01, 1.0 - it / iterations)
        move = rng.random()
        new_cuts = list(cuts)
        if move < 0.6 and new_cuts:
            k = rng.randrange(len(new_cuts))
            new_cuts[k] += rng.choice((-3, -2, -1, 1, 2, 3))
        elif move < 0.8 and len(new_cuts) > 1:
            del new_cuts[rng.randrange(len(new_cuts))]
        else:
            new_cuts.append(rng.randint(lo, S - lo))
        new_cuts = sorted(set(c for c in new_cuts if 0 < c < S))
        spans = staple_spans(new_cuts)
        if any((b - a) < lo or (b - a) > hi for a, b in spans):
            continue
        new_score, seqs, counts = evaluate(new_cuts)
        d = new_score - cur_score
        if d < 0 or rng.random() < math.exp(-d / (temp * 5.0)):
            cuts = new_cuts
            cur_score = new_score
            if new_score < best_score:
                best_score, best_seqs, best_counts = new_score, seqs, counts
                best_cuts = list(new_cuts)
        history.append(cur_score)

    # Deterministic Tm-equalisation refinement (cooperative annealing): a focused local
    # search that nudges cuts to tighten the staple Tm spread. It preserves the hard
    # guarantees (length window, boundary coverage, loop balance, off-target), but tightening
    # the Tm STDEV is only ONE term of the objective -- pushing it past the model's optimum
    # can raise the Tm-WINDOW penalty (staples driven out of [tm_lo, tm_hi]) by more than the
    # variance penalty falls, which NET-WORSENS predicted yield. Measured: gating acceptance
    # on Tm-stdev alone degraded the proxy in 12/12 small-shape cases (tetra/cube/octa/square)
    # by +4..+9, helping only the two largest presets. Since Tm variance is ALREADY weighted
    # in score_set (w_tm_var), the consistent rule is to keep the refinement only when it
    # improves the FULL objective -- so it acts as a deterministic refiner that can never
    # worsen the design. (To value uniformity more, raise w_tm_var in the model and
    # re-validate; don't let a post-pass silently override the calibrated objective.)
    if best_cuts:
        refined = equalize_tm(template, best_cuts, xovers_t, model,
                              offtarget_mask=offtarget_mask)
        if refined != best_cuts and length_valid(refined):
            r_score, r_seqs, r_counts = evaluate(refined)
            if r_score < best_score - 1e-9:
                best_cuts, best_seqs, best_counts = refined, r_seqs, r_counts
                best_score = r_score
                history.append(best_score)

    return best_cuts, best_seqs, best_counts, history
