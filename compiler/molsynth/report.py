"""
Yield diagnostic for a compiled design.

Emits the diagnostic the literature recommends for judging a design BEFORE ordering
oligos (Aksel et al. 2024 plot a per-staple folding-temperature histogram; a tight,
unimodal distribution near the target means the staples cross their folding transition
together = cooperative, high-yield annealing). We add the crossover/loop-closure
distribution (the other yield lever) and the optimizer's score improvement.
"""

from __future__ import annotations

from . import sequences as sq
from . import mechanics as mech

BP_NM = 0.34   # rise per base pair, B-form DNA


def _reality_check(design: dict, staples) -> str:
    """Adversarial physics/materials audit: the failure modes that break the REAL build even
    when the compile 'succeeds'. Report-only (does not change any orderable output)."""
    approx_nm = design.get("approx_nm") or 0
    max_edge_bp = approx_nm / BP_NM if approx_nm else 0
    n_helices = int(design.get("edge_helices", 1) or 1)
    v = mech.stiffness_verdict(max_edge_bp, n_helices)
    bend = v["rms_bend_deg"]
    lp_um = v["lp_nm"] / 1000.0
    if n_helices <= 1:
        bundle_desc = "single B-DNA duplex"
    else:
        bundle_desc = (f"{n_helices}-helix bundle (Lp~{lp_um:.2g} um, "
                       f"{v['ei_ratio']:.0f}x stiffer than one duplex)")
    if v["category"] == "rigid":
        stiff = (f"rigid (edge << persistence length, Lp~{lp_um:.2g} um) -> holds its designed "
                 "shape")
    elif v["category"] == "semi-rigid":
        stiff = "semi-rigid -> minor vertex-angle fluctuation"
    else:
        stiff = ("FLOPPY: single-duplex edges fluctuate >25 deg rms -> the wireframe breathes; "
                 "for a rigid shape set edge_helices>=3 (multi-helix bundle, 6HB Lp ~1-10 um) or "
                 "accept an ensemble-averaged shape (intended for DAEDALUS-style compliant "
                 "wireframes)")

    seqs = [getattr(s, "seq", "") for s in staples]
    g4 = sum(sq.g_quadruplex_sites(s) for s in seqs)
    g4_line = (f"{g4} staple(s) with a G-quadruplex motif -> sequestered from folding; redesign"
               if g4 else "0 G-quadruplex motifs -> clean (audited)")

    tms = [s.tm_C for s in staples]                       # already at the buffer salt (0.166)
    na50 = [sq.tm(s, na_M=0.05) for s in seqs if s]       # textbook 50 mM Na+, for contrast
    delta = (sum(tms) / len(tms) - sum(na50) / len(na50)) if (tms and na50) else 0.0

    return f"""## Physics & materials reality check (adversarial)
_Failure modes that break the physical build even when the compile succeeds. Verify these,
not just that files were written._
- edge stiffness (edge_helices={n_helices}): longest edge ~{max_edge_bp:.0f} bp (~{approx_nm} nm);
  {bundle_desc} RMS thermal bend ~{bend:.0f} deg (worm-like chain) -> {stiff}
- sequence liability: {g4_line}
- buffer Tm: the Tm histogram above is at the real ~12.5 mM Mg2+ folding-buffer salt
  ([Na+]_eq=0.166; Owczarzy 2008, research/exp1) -- ~{delta:+.1f} C vs the 50 mM-Na textbook
  value. The anneal-ramp top end should clear the hottest staple's Tm.
- kinetic blind spot: this score is THERMODYNAMIC (equilibrium Tm). Folding is kinetic --
  if hot staples close loops before the structure nucleates, yield drops despite good Tm.
  Mitigate with the Mg2+ x ramp screen (screen.md); program nucleation seams last.
"""


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

    # routing topology / A-trail quality (measured, not claimed)
    ff = design.get("routing_face_follow_fraction")
    vx = design.get("routing_vertex_crossings")
    phase = design.get("crossover_phase_max_bp")
    phase_line = ""
    if phase is not None:
        verdict = ("in-phase (DAEDALUS rule: edges are integer helical turns)"
                   if phase <= 0.75 else
                   "some edges off integer turns -> crossover phase slip; oxDNA relax advised")
        phase_line = (f"\n- crossover phase (measured): worst edge {phase:.2f} bp from an "
                      f"integer 10.5-bp turn -> {verdict}")
    if ff is None:
        routing_block = ("- single closed scaffold circuit: "
                         f"{design.get('single_scaffold_circuit')} (every edge twice)"
                         + phase_line +
                         "\n- A-trail metric: n/a (mesh has no faces; arbitrary single circuit)")
    else:
        routing_block = (
            f"- single closed scaffold circuit: {design.get('single_scaffold_circuit')} "
            "(machine-checked: closed + complete + both directions of every edge)\n"
            f"- A-trail quality (measured): non-crossing adjacent-edge turn at {ff:.0%} of "
            f"vertex passages; {vx} true crossing(s)\n"
            "  (the router searches for the fewest crossings -- on the Platonic presets it "
            "reaches 1-2;\n"
            "   for a formally GUARANTEED non-crossing A-trail, route the PLY wireframe "
            "through PERDIX/DAEDALUS)"
            + phase_line)

    return f"""# Yield diagnostic - {design.get('design_name','design')}

_Pre-order design check. See docs/research/06-ai-staple-optimizer.md. This predicts
cooperativity from sequence thermodynamics; it does not replace a wet-lab Mg2+ x ramp
screen, and absolute Tm depends on the assumed salt/concentration._

## Routing topology
{routing_block}

## Optimizer
- objective: {s0} -> {s1}{improve}
- staples: {st.get('n_staples')}  (crossover-bridging {st.get('n_crossover_staples')},
  overloaded >2 crossovers: {st.get('n_overloaded_staples', 0)})
- off-target screen: longest scaffold-repeat inside a staple = {st.get('offtarget_max', 0)} nt;
  staples with >14 nt repeat (off-target risk) = {st.get('n_offtarget_risk', 0)}
- staple cross-dimer screen: worst staple-staple complement = {st.get('dimer_max_cross_dimer', 0)} nt
  in {st.get('dimer_n_dimer_pairs', 0)} flagged pair(s) (>=8 nt); <=~10 nt is benign

## Per-staple melting-temperature histogram (deg C)
mean {st.get('tm_mean_C')}  stdev {spread}  range {st.get('tm_min_C')}-{st.get('tm_max_C')}
{_ascii_hist(tms, lo, hi)}

-> {verdict}

## Crossover / loop-closure distribution per staple (Aksel 2024: keep <= 2)
{xrows}

## Length distribution
min {st.get('len_min')}  mean {st.get('len_mean')}  max {st.get('len_max')} nt (target 32-42)

{_reality_check(design, staples)}"""
