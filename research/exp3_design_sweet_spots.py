"""
Experiment 3 — where the compiler's design levers actually pay off (engineering sweet spots).

Two measured questions about compiler/molsynth's yield optimiser:

  (A) SCAFFOLD-OFFSET LANDSCAPE.  M13mp18 is a circular scaffold, so where the route STARTS
      is a free design choice. compile_shape() searches 8 evenly-spaced offsets and keeps the
      best. Is that worth it?  We sweep many offsets, score each with the same cheap proxy the
      compiler uses, and report the spread (best vs worst) = the yield-proxy lever available
      for free, plus whether 8 samples reliably catch the optimum.

  (B) OBJECTIVE ABLATION.  The optimiser balances many molecular terms (Tm window + spread,
      loop-closure entropy [Aksel 2024], off-target repeats, hairpins, ...). Which ones are
      doing real work for the M13 sequence?  We anneal once per term-removed model and measure
      how the resulting design degrades under the FULL (default) objective — big degradation =
      a term that matters here; ~0 = a term that is slack for this scaffold/shape.

Run:  python research/exp3_design_sweet_spots.py [shape]   (default octahedron)
Uses the molsynth API directly; pure stdlib.
"""
from __future__ import annotations

import math
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "compiler"))

from molsynth import geometry                       # noqa: E402
from molsynth import scaffold as scaffold_mod        # noqa: E402
from molsynth import sequences as sq                 # noqa: E402
from molsynth.optimizer import YieldModel, proxy_score, anneal  # noqa: E402

SHAPE = sys.argv[1] if len(sys.argv) > 1 else "octahedron"
MIN_EDGE_BP = 42


def _rotate(s, off):
    off %= len(s)
    return s if off == 0 else s[off:] + s[:off]


def design_metrics(seqs, model):
    tms = [sq.tm(s, **model.tm_kwargs) for s in seqs]
    tms = [t for t in tms if not math.isnan(t)]
    return {
        "n": len(seqs),
        "tm_mean": statistics.mean(tms) if tms else float("nan"),
        "tm_sd": statistics.pstdev(tms) if len(tms) > 1 else 0.0,
        "len_min": min(len(s) for s in seqs), "len_max": max(len(s) for s in seqs),
    }


def main():
    print(f"shape = {SHAPE}\n")
    mesh = geometry.load_shape(SHAPE)
    seq, sc_name, synthetic = scaffold_mod.load_scaffold()
    model = YieldModel()

    # ---- (A) scaffold-offset landscape -------------------------------------------------
    N = 24
    offsets = [i * len(seq) // N for i in range(N)]
    scores = []
    for off in offsets:
        rot = _rotate(seq, off)
        r = scaffold_mod.route(mesh, rot, sc_name, synthetic, min_edge_bp=MIN_EDGE_BP)
        mask = sq.repeat_mask(rot)[:len(r.scaffold_seq)]
        scores.append(proxy_score(r, model, offtarget_mask=mask))
    best, worst, med = min(scores), max(scores), statistics.median(scores)
    # would the compiler's 8-sample search catch the optimum? compare best-of-8 to best-of-24
    best8 = min(scores[i] for i in range(0, N, N // 8))
    print("=== (A) scaffold-offset landscape (proxy score, lower=better) ===")
    print(f"  {N} offsets:  best={best:.2f}  median={med:.2f}  worst={worst:.2f}  "
          f"spread={worst-best:.2f}")
    print(f"  best-of-8 (compiler's search) = {best8:.2f}   gap to global best = {best8-best:+.2f}")
    print(f"  -> the circular start is a FREE lever worth ~{worst-best:.1f} proxy units; "
          f"8 samples land within {best8-best:.2f} of optimum.\n")

    # ---- (B) objective ablation --------------------------------------------------------
    rot = _rotate(seq, 0)
    routing = scaffold_mod.route(mesh, rot, sc_name, synthetic, min_edge_bp=MIN_EDGE_BP)
    mask = sq.repeat_mask(rot)[:len(routing.scaffold_seq)]
    template = sq.reverse_complement(routing.scaffold_seq)
    xs = routing.crossover_positions

    def run(weight_overrides):
        m = YieldModel()
        for k, v in (weight_overrides or {}).items():
            m.weights[k] = v
        cuts, seqs, counts, hist = anneal(template, xs, m, iterations=3000,
                                          offtarget_mask=mask)
        # score the resulting design under the FULL default objective
        full = YieldModel()
        spans, prev = [], 0
        for c in list(cuts) + [len(template)]:
            spans.append((prev, c)); prev = c
        loops, cov = [], set()
        from molsynth.optimizer import boundaries_in
        xs_t = sorted(len(template) - p for p in xs if 0 < p < len(template))
        offt = []
        for a, b in spans:
            bnds = boundaries_in(a, b, xs_t); cov.update(bnds)
            pts = [a] + bnds + [b]
            loops += [pts[i] - pts[i-1] for i in range(1, len(pts))]
            offt.append(sq.longest_run(mask, len(template)-b, len(template)-a))
        score = full.score_set(seqs, counts, loops, len(xs_t), len(cov), offtarget_runs=offt)
        return score, design_metrics(seqs, full)

    base_score, base_m = run(None)
    print("=== (B) objective ablation (octahedron, scored under FULL objective) ===")
    print(f"  baseline: full-score={base_score:.2f}  n={base_m['n']}  "
          f"Tm={base_m['tm_mean']:.1f}+/-{base_m['tm_sd']:.1f}C  "
          f"len {base_m['len_min']}-{base_m['len_max']}")
    ablations = [
        ("no Tm-variance term",  {"w_tm_var": 0.0}),
        ("no Tm-window term",    {"w_tm": 0.0}),
        ("no loop-entropy term", {"w_loop_entropy": 0.0}),
        ("no off-target term",   {"w_offtarget": 0.0}),
        ("no hairpin term",      {"w_hairpin": 0.0}),
        ("no repeat term",       {"w_repeat": 0.0}),
    ]
    print(f"  {'ablation':24}{'full-score':>12}{'d vs base':>11}{'Tm sd':>9}")
    for name, ov in ablations:
        s, m = run(ov)
        print(f"  {name:24}{s:>12.2f}{s-base_score:>+11.2f}{m['tm_sd']:>8.1f}C")
    print("  (positive d = removing that term gave a design the full objective likes LESS,")
    print("   i.e. the term was doing real work for this scaffold/shape; ~0 = slack here.)")


if __name__ == "__main__":
    main()
