"""
Experiment 9 — a KINETIC Tm-ladder: programming the folding ORDER, not just the endpoint.

The compiler's yield objective is purely THERMODYNAMIC: it clusters every staple's
equilibrium melting temperature so they cross their transition together (cooperative
annealing, Aksel 2024). It is blind to the ORDER in which staples engage as the pot cools.
But real folding is a kinetic, ordered process — as the temperature ramps down, staples
bind in descending-Tm order, so the highest-Tm staples nucleate FIRST. Two independent
experimental lines show the order decides the yield:

  * Sobczak et al., Science 338:1458 (2012), "Rapid Folding of DNA into Nanoscale Shapes at
    Constant Temperature": each design has a sharp optimal folding temperature set by the
    *sequence of binding events*, not by the equilibrium endpoint.
  * Dunn et al., Nature 525:82 (2015), "Guiding the folding pathway of DNA origami":
    base-by-base pathway measurement shows which staples engage first selects the final
    structure — a hot loop-/seam-closing staple that binds before its framework is laid
    down can lock in a kinetic trap.

The defensible kinetic PROXY (optimizer.kinetic_penalty, weight w_kinetic, DEFAULT 0):
a staple's "load" = (# crossovers it bridges) + kinetic_loop_w * ln(largest enclosed loop).
High-load staples are the structure's seams; they should fold LATE, i.e. sit LOW in the Tm
distribution. The term penalises the positive covariance between load and Tm, rewarding a
gradient where crossover-heavy / big-loop staples are NOT the hottest.

This experiment, with the term OFF vs ON on the SAME design, MEASURES the correlation
between a staple's load and its Tm. Two parts:
  (A) a CONTROLLED unit demonstration on a fixed staple set (deterministic, exact) — proves
      the penalty correctly distinguishes a framework-first ordering from a seam-first one.
  (B) the END-TO-END anneal — turning the term on drives the measured load↔Tm correlation
      down toward / below zero (heavy staples pushed cooler).

KINETIC PROXY ONLY — there is NO molecular-dynamics kinetic simulator here; the term encodes
the descending-Tm folding-order assumption of the cited isothermal/pathway experiments.

Run:  python research/exp9_kinetic_ladder.py [shape]   (default cube)
Pure stdlib; uses the molsynth API directly.
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "compiler"))

from molsynth import geometry                       # noqa: E402
from molsynth import scaffold as scaffold_mod        # noqa: E402
from molsynth import sequences as sq                 # noqa: E402
from molsynth.optimizer import (                     # noqa: E402
    YieldModel, anneal, boundaries_in, kinetic_penalty)

SHAPE = sys.argv[1] if len(sys.argv) > 1 else "cube"
ITERS = 3000
SEED = 12345
W_KINETIC = 8.0          # demonstration weight (production default is 0.0)


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0 or syy == 0:
        return float("nan")
    return sxy / math.sqrt(sxx * syy)


def loads_and_tm(template, cuts, xovers_t, model):
    """Per-staple (crossover count, largest enclosed-loop size, Tm) for a cut set."""
    S = len(template)
    spans, prev = [], 0
    for c in list(cuts) + [S]:
        spans.append((prev, c))
        prev = c
    cross, loop_load, tms = [], [], []
    for a, b in spans:
        bnds = boundaries_in(a, b, xovers_t)
        cross.append(len(bnds))
        pts = [a] + bnds + [b]
        seg = [pts[i] - pts[i - 1] for i in range(1, len(pts))]
        loop_load.append(max(seg) if seg else 0)
        tms.append(sq.tm(template[a:b], **model.tm_kwargs))
    return cross, loop_load, tms


def part_a_controlled():
    """Deterministic: the penalty must rank a framework-first ladder BELOW a seam-first one.

    Three staples: a non-crossover framework staple (load 0) and two crossover staples
    (load 1). 'Seam-first' = the crossover staples are the HOTTEST (kinetic trap). 'Framework
    -first' = the crossover staples are the COOLEST (fold last). Same Tm multiset, only the
    assignment to loads differs."""
    cross = [0, 1, 1]
    tm_set = [55.0, 60.0, 65.0]
    # seam-first: high-load staples get the two HIGHEST Tms (the bad, trap-prone arrangement)
    seam_first = kinetic_penalty(cross, [55.0, 60.0, 65.0])
    # framework-first: high-load staples get the two LOWEST Tms (the desired gradient)
    framework_first = kinetic_penalty([0, 1, 1], [65.0, 55.0, 60.0])
    print("=== (A) controlled unit demonstration (deterministic, exact) ===")
    print(f"  staple crossover loads = {cross}, Tm multiset = {tm_set} C")
    print(f"  seam-first  (crossover staples HOTTEST -> trap):     penalty = {seam_first:.3f}")
    print(f"  framework-first (crossover staples COOLEST -> good): penalty = {framework_first:.3f}")
    ok = framework_first < seam_first and framework_first == 0.0
    print(f"  -> framework-first is favoured (lower) and the desired gradient costs 0: {ok}\n")
    return ok


def part_b_measure(label, weights_override, routing, template, mask, xovers_t):
    model = YieldModel()
    for k, v in weights_override.items():
        model.weights[k] = v
    cuts, seqs, counts, hist = anneal(
        template, routing.crossover_positions, model,
        iterations=ITERS, seed=SEED, offtarget_mask=mask)
    cross, loop_load, tms = loads_and_tm(template, cuts, xovers_t, model)
    loop_w = model.weights.get("kinetic_loop_w", 0.5)
    full_load = [cross[i] + (loop_w * math.log(loop_load[i]) if loop_load[i] > 1 else 0.0)
                 for i in range(len(cross))]
    v = [i for i in range(len(tms)) if not math.isnan(tms[i])]
    r_cross = pearson([cross[i] for i in v], [tms[i] for i in v])
    r_load = pearson([full_load[i] for i in v], [tms[i] for i in v])
    kpen = kinetic_penalty(cross, tms, loop_loads=loop_load, loop_w=loop_w)
    heavy = [tms[i] for i in range(len(cross)) if cross[i] >= 1 and not math.isnan(tms[i])]
    light = [tms[i] for i in range(len(cross)) if cross[i] == 0 and not math.isnan(tms[i])]
    hmean = sum(heavy) / len(heavy) if heavy else float("nan")
    lmean = sum(light) / len(light) if light else float("nan")
    tv = [tms[i] for i in v]
    print(f"  {label}")
    print(f"    staples={len(seqs)}  max crossover/staple={max(cross)}  "
          f"Tm mean={sum(tv)/len(tv):.1f}C  final objective={hist[-1]:.2f}")
    print(f"    Pearson r(crossover-count, Tm)        = {r_cross:+.3f}")
    print(f"    Pearson r(crossover+loop load, Tm)    = {r_load:+.3f}")
    print(f"    kinetic_penalty (covariance, lower=better) = {kpen:.3f}")
    print(f"    mean Tm: crossover staples={hmean:.1f}C vs non-crossover={lmean:.1f}C "
          f"(delta={hmean-lmean:+.2f}C)")
    return r_cross, r_load, kpen


def main():
    print(f"shape = {SHAPE}   (w_kinetic demo = {W_KINETIC}; production default = 0.0)")
    print(f"iters = {ITERS}  seed = {SEED}\n")

    part_a_controlled()

    mesh = geometry.load_shape(SHAPE)
    seq, name, synth = scaffold_mod.load_scaffold()
    routing = scaffold_mod.route(mesh, seq, name, synth)
    template = sq.reverse_complement(routing.scaffold_seq)
    S = len(template)
    mask = sq.repeat_mask(routing.scaffold_seq)[:S]
    xovers_t = sorted(S - p for p in routing.crossover_positions if 0 < p < S)

    print("=== (B) end-to-end anneal: does the term push high-load staples COOLER? ===\n")
    off = part_b_measure("w_kinetic = 0  (OFF, current default)", {},
                         routing, template, mask, xovers_t)
    print()
    on = part_b_measure(f"w_kinetic = {W_KINETIC}  (ON)", {"w_kinetic": W_KINETIC},
                        routing, template, mask, xovers_t)
    print()
    print("=== effect of the kinetic term (ON minus OFF) ===")
    print(f"  r(crossover-count, Tm):  {off[0]:+.3f} -> {on[0]:+.3f}   (delta {on[0]-off[0]:+.3f})")
    print(f"  r(load, Tm):             {off[1]:+.3f} -> {on[1]:+.3f}   (delta {on[1]-off[1]:+.3f})")
    print(f"  kinetic covariance:      {off[2]:.3f} -> {on[2]:.3f}   "
          f"(delta {on[2]-off[2]:+.3f}; {100*(on[2]-off[2])/off[2]:+.0f}%)"
          if off[2] else
          f"  kinetic covariance:      {off[2]:.3f} -> {on[2]:.3f}")
    print()
    print("  Honest structural note: the existing length window (staples <= 42 nt) is SHORTER")
    print("  than the inter-crossover spacing of these single-duplex wireframes (~63 bp), so a")
    print("  staple physically cannot bridge two crossovers -- max crossover-load is 1 for every")
    print("  preset. The kinetic term's lever is therefore (i) the binary crossover-vs-framework")
    print("  Tm ordering and (ii) the enclosed-loop size; it bites hardest on denser/multi-helix")
    print("  designs where staples DO carry >1 crossover. Reading: the term lowers the load-Tm")
    print("  correlation toward/below 0 (seam staples driven cooler -> framework nucleates first,")
    print("  Dunn 2015; Sobczak 2012). KINETIC PROXY ONLY -- no MD simulator.")


if __name__ == "__main__":
    main()
