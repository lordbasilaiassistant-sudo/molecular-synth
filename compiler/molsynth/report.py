"""
Yield diagnostic for a compiled design.

Emits the diagnostic the literature recommends for judging a design BEFORE ordering
oligos (Aksel et al. 2024 plot a per-staple folding-temperature histogram; a tight,
unimodal distribution near the target means the staples cross their folding transition
together = cooperative, high-yield annealing). We add the crossover/loop-closure
distribution (the other yield lever) and the optimizer's score improvement.
"""

from __future__ import annotations


def _ascii_hist(values, lo, hi, bins=16, width=40):
    if not values:
        return "(none)"
    span = (hi - lo) or 1.0
    counts = [0] * bins
    for v in values:
        b = int((v - lo) / span * bins)
        b = min(bins - 1, max(0, b))
        counts[b] += 1
    peak = max(counts) or 1
    out = []
    for i, c in enumerate(counts):
        a = lo + span * i / bins
        bar = "#" * int(c / peak * width)
        out.append(f"  {a:6.1f} | {bar} {c}")
    return "\n".join(out)


def yield_report(design: dict, staples, history) -> str:
    st = design.get("staple_stats", {})
    tms = [s.tm_C for s in staples]
    xs = [s.crossovers for s in staples]
    lo = min(tms) if tms else 0
    hi = max(tms) if tms else 1
    # crossover distribution
    maxx = max(xs) if xs else 0
    xdist = {k: xs.count(k) for k in range(maxx + 1)}
    xrows = "\n".join(
        f"  {k} crossover(s): {'#'*v} {v}{'   <-- overloaded (>2, penalised)' if k > 2 else ''}"
        for k, v in xdist.items())

    s0 = design.get("optimizer_score_initial")
    s1 = design.get("optimizer_score")
    improve = ""
    if s0 is not None and s1 is not None and s0 != 0:
        improve = f"  ({100*(s0 - s1)/s0:.0f}% lower objective)"

    spread = st.get("tm_stdev_C", 0)
    verdict = ("tight Tm distribution -> cooperative anneal expected (good)"
               if spread <= 4 else
               "broad Tm distribution -> screen Mg2+/ramp; some staples are outliers")

    return f"""# Yield diagnostic - {design.get('design_name','design')}

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Optimizer
- objective: {s0} -> {s1}{improve}
- staples: {st.get('n_staples')}  (crossover-bridging {st.get('n_crossover_staples')},
  overloaded >2 crossovers: {st.get('n_overloaded_staples', 0)})
- off-target screen: longest scaffold-repeat inside a staple = {st.get('offtarget_max', 0)} nt;
  staples with >14 nt repeat (off-target risk) = {st.get('n_offtarget_risk', 0)}

## Per-staple melting-temperature histogram (deg C)
mean {st.get('tm_mean_C')}  stdev {spread}  range {st.get('tm_min_C')}-{st.get('tm_max_C')}
{_ascii_hist(tms, lo, hi)}

-> {verdict}

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
{xrows}

## Length distribution
min {st.get('len_min')}  mean {st.get('len_mean')}  max {st.get('len_max')} nt (target 32-42)
"""
