"""
Edge mechanics: stiffness as a first-class design dial.

A single B-DNA duplex has a persistence length Lp ~= 50 nm (~147 bp). A wireframe edge
much longer than Lp bends under thermal forces (<theta^2> = L/Lp), so a single-duplex
polyhedron with ~63 bp edges is intentionally COMPLIANT (it samples an ensemble of shapes,
not one rigid frame -- see research/exp6 F1). The remedy used by every rigid DNA-origami
object is to replace each single duplex with a MULTI-HELIX BUNDLE: several parallel duplexes
held together by inter-helix crossovers. Bundles are tens-to-hundreds of times stiffer.

Model (parallel-axis bundle beam, with a crossover-compliance knockdown)
-----------------------------------------------------------------------
Treat each helix as a thin rod (cross-sectional second moment I0 = pi r^4 / 4, area
A = pi r^2). The bundle's bending rigidity is the sum of each helix's own I0 plus its
parallel-axis contribution A * d_i^2 (d_i = distance of helix i from the bundle centroid):

    EI_bundle / EI_single  =  N  +  alpha * (A / I0) * sum_i d_i^2
                           =  N  +  alpha * (4 / r^2) * sum_i d_i^2

with helix radius r ~= 1.0 nm and honeycomb/square inter-helix spacing s ~= 2.6 nm
(the standard origami lattice). Lp scales with EI, so Lp_bundle = Lp_single * EI_ratio,
and the WLC RMS bend is theta_rms = sqrt(L / Lp_bundle).

alpha (0 < alpha <= 1) is a crossover-compliance knockdown: a rigidly-fused solid beam
would have alpha = 1, but real bundles are softer because the inter-helix crossovers allow
some shear between helices. We calibrate alpha = 0.60 so the 6-helix bundle lands at
Lp ~= 5 um -- the value MEASURED for a 6HB by Kauert 2011 -- which sits squarely inside the
1-10 um literature range. The single duplex is anchored exactly at Lp = 50 nm (147 bp) by
construction (the off-axis term vanishes for N = 1).

References:
  Hagerman, Annu. Rev. Biophys. Biophys. Chem. 17:265 (1988)  -- dsDNA Lp ~ 50 nm.
  Kauert, Nelson, Rief & Seidel, Nano Lett. 11:5558 (2011)    -- 6HB Lp ~ 5 um (measured).
  Bai, Martin, Scheres & Dietz, PNAS 109:20012 (2012)         -- bundle rigidity / cryo-EM.
  Dietz, Douglas & Shih, Science 325:725 (2009)               -- multilayer bundles are rigid.
"""

from __future__ import annotations

import math

from . import sequences as sq

# Geometry / calibration constants
HELIX_RADIUS_NM = 1.0      # effective B-DNA helix radius (incl. ~half hydration shell)
HELIX_SPACING_NM = 2.6     # inter-helix spacing on the honeycomb/square origami lattice
CROSSOVER_KNOCKDOWN = 0.60  # alpha: shear compliance vs a rigidly-fused solid beam (Kauert 2011)
LP_SINGLE_BP = 147.0        # dsDNA Lp ~50 nm ~= 147 bp (matches sequences.wlc_rms_bend_deg default)


def _bundle_coords(n_helices: int):
    """Helix-centre (x, y) coordinates (nm) for the standard origami cross-sections.

    Uses the lattices real designs use: a line for 2, a triangle/square for 3-4, a hexagon
    ring for the 6-helix bundle (6HB), and a packed ring fallback for other counts. Only the
    spread of the helices about the centroid matters for bending, so a regular arrangement
    is the right canonical choice."""
    if n_helices <= 1:
        return [(0.0, 0.0)]
    s = HELIX_SPACING_NM
    if n_helices == 2:
        return [(0.0, 0.0), (s, 0.0)]
    if n_helices == 3:
        return [(0.0, 0.0), (s, 0.0), (s / 2.0, s * math.sqrt(3) / 2.0)]
    if n_helices == 4:
        return [(0.0, 0.0), (s, 0.0), (0.0, s), (s, s)]
    if n_helices == 6:
        # 6HB: six helices on a hexagonal ring (the canonical rigid bundle)
        return [(s * math.cos(math.radians(60 * k)),
                 s * math.sin(math.radians(60 * k))) for k in range(6)]
    # generic fallback: helices evenly on a ring of radius scaled to keep ~s spacing
    radius = s / (2.0 * math.sin(math.pi / n_helices))
    return [(radius * math.cos(2 * math.pi * k / n_helices),
             radius * math.sin(2 * math.pi * k / n_helices)) for k in range(n_helices)]


def bundle_ei_ratio(n_helices: int) -> float:
    """EI_bundle / EI_single for an `n_helices` bundle (the stiffness multiplier).

    Parallel-axis: N (each helix's own moment) + alpha * (4/r^2) * sum d_i^2 (off-axis term).
    Monotonically increasing in n_helices; equals 1.0 for a single duplex."""
    n = max(1, int(n_helices))
    if n == 1:
        return 1.0
    coords = _bundle_coords(n)
    cx = sum(p[0] for p in coords) / n
    cy = sum(p[1] for p in coords) / n
    sum_d2 = sum((p[0] - cx) ** 2 + (p[1] - cy) ** 2 for p in coords)
    return n + CROSSOVER_KNOCKDOWN * (4.0 / HELIX_RADIUS_NM ** 2) * sum_d2


def bundle_lp_bp(n_helices: int) -> float:
    """Effective persistence length (in bp) of an `n_helices` bundle edge."""
    return LP_SINGLE_BP * bundle_ei_ratio(n_helices)


def bundle_lp_nm(n_helices: int) -> float:
    """Effective persistence length in nm (0.34 nm/bp)."""
    return bundle_lp_bp(n_helices) * 0.34


def edge_rms_bend_deg(length_bp: float, n_helices: int = 1) -> float:
    """RMS thermal bend (deg) of an edge of `length_bp` built from `n_helices` duplexes.

    For n_helices == 1 this is exactly sequences.wlc_rms_bend_deg(length_bp) (single duplex,
    Lp ~50 nm). For a bundle, Lp is scaled by bundle_ei_ratio(n_helices), so the edge bends
    less: <theta^2> = L / Lp_bundle. Monotonically DECREASING in n_helices."""
    return sq.wlc_rms_bend_deg(length_bp, lp_bp=bundle_lp_bp(n_helices))


def stiffness_verdict(length_bp: float, n_helices: int = 1) -> dict:
    """Full stiffness readout for an edge: bend, Lp, EI ratio, and a categorical verdict.

    Verdict thresholds match report._reality_check: <=10 deg rigid, <=25 deg semi-rigid,
    else floppy."""
    bend = edge_rms_bend_deg(length_bp, n_helices)
    if bend <= 10:
        category = "rigid"
    elif bend <= 25:
        category = "semi-rigid"
    else:
        category = "floppy"
    return {
        "length_bp": length_bp,
        "n_helices": int(n_helices),
        "ei_ratio": bundle_ei_ratio(n_helices),
        "lp_bp": bundle_lp_bp(n_helices),
        "lp_nm": bundle_lp_nm(n_helices),
        "rms_bend_deg": bend,
        "category": category,
    }
