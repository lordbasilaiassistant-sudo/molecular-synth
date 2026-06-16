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
deterministic alternative used by pyOrigamiBreak).

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
    "tm_lo": 50.0, "tm_hi": 64.0,
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
}


@dataclass
class YieldModel:
    weights: dict = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    tm_kwargs: dict = field(default_factory=dict)

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

    def score_set(self, staple_seqs, cross_counts, loop_sizes, n_boundaries, n_covered):
        """Total objective for a full staple set (lower is better).

        staple_seqs   : list of staple sequences
        cross_counts  : crossovers (vertex boundaries) each staple bridges
        loop_sizes    : flat list of enclosed-loop sizes (bases) across all staples
        n_boundaries  : total vertex/crossover boundaries in the design
        n_covered     : how many of those boundaries are bridged by >=1 staple
        """
        if not staple_seqs:
            return 1e9
        w = self.weights
        total = 0.0
        tms = []
        for seq, c in zip(staple_seqs, cross_counts):
            total += self.staple_seq_penalty(seq)
            if c > w["xmax"]:                       # too many loop closures (Aksel 2024)
                total += w["w_loop"] * (c - w["xmax"])
            t = sq.tm(seq, **self.tm_kwargs)
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
        return total


def boundaries_in(start, end, xovers):
    """Vertex boundaries strictly inside the half-open interval [start, end)."""
    return [c for c in xovers if start < c < end]


def anneal(template, crossover_positions_scaffold, model: YieldModel,
           iterations=4000, seed=12345, target_len=37):
    """Simulated annealing over the cut positions of the staple template.

    template : reverse complement of the scaffold route (the staple strand, 5'->3').
    crossover_positions_scaffold : vertex boundaries in SCAFFOLD coordinates.
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
        seqs, counts, loops = [], [], []
        covered = set()
        for a, b in spans:
            seqs.append(template[a:b])
            bnds = boundaries_in(a, b, xovers_t)
            counts.append(len(bnds))
            covered.update(bnds)
            # enclosed-loop sizes = gaps between consecutive bridged boundaries
            pts = [a] + bnds + [b]
            for i in range(1, len(pts)):
                loops.append(pts[i] - pts[i - 1])
        score = model.score_set(seqs, counts, loops, n_boundaries, len(covered))
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

    return best_cuts, best_seqs, best_counts, history
