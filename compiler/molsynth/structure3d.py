"""
3D structure generation.

Turns the (topological) routing + staples into explicit 3D coordinates for every
nucleotide, so the design stops being "just sequences" and becomes a structure you can
VISUALISE (oxView / ChimeraX / PyMOL) and RELAX / SIMULATE (oxDNA).

Model: each wireframe edge is rendered as B-form duplex(es) running along the edge.
The whole mesh is scaled so an edge's geometric length ~ its base-pair length x rise,
so vertices roughly meet and bond lengths are ~physical (a good oxDNA starting config;
run an oxDNA min/relax to clean up vertex junctions and crossovers). The scaffold is
laid as one continuous strand along its Eulerian route; each staple nucleotide is
placed as the Watson-Crick partner of its scaffold base (opposite backbone of the same
duplex), so scaffold and staples form real duplexes.

We emit:
  * a single ORDERED nucleotide list (same order as the oxDNA .top), used to write a
    consistent topology + configuration pair, and
  * helper geometry so export.py can write conf.dat (oxDNA) and structure.pdb.

oxDNA orientation convention: a1 = base vector (backbone -> base / toward the pairing
partner), a3 = stacking/helix-axis direction (the strand's 3' sense); a2 = a3 x a1 is
implied. We output a1, a3 as orthonormal unit vectors. Units are oxDNA simulation units
(1 u ~ 0.8518 nm).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import sequences as sq

# oxDNA-ish helix geometry (simulation units)
RISE = 0.40            # base-base spacing along the helix axis
BACKBONE_R = 0.60      # COM offset from helix centre toward the backbone
TWIST = 0.6283         # radians per base (~36 deg, right-handed B-helix)
INTERHELIX = 2.6       # spacing between the two duplexes of one DX edge
PAD = 20.0             # box padding


# --------------------------------------------------------------------------- #
# tiny vector helpers (tuples of 3 floats)
# --------------------------------------------------------------------------- #
def _add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _scale(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _norm(a):
    return math.sqrt(_dot(a, a))


def _unit(a):
    n = _norm(a)
    return (a[0] / n, a[1] / n, a[2] / n) if n > 1e-12 else (1.0, 0.0, 0.0)


def _any_perp(axis):
    """A unit vector perpendicular to axis."""
    ref = (0.0, 0.0, 1.0) if abs(axis[2]) < 0.9 else (1.0, 0.0, 0.0)
    return _unit(_cross(axis, ref))


def _rotate(v, axis, ang):
    """Rodrigues rotation of v about unit axis by ang radians."""
    c, s = math.cos(ang), math.sin(ang)
    return _add(_add(_scale(v, c), _scale(_cross(axis, v), s)),
                _scale(axis, _dot(axis, v) * (1 - c)))


@dataclass
class Nuc:
    strand: int           # 1 = scaffold, 2.. = staples
    base: str
    n3: int               # global index of 3' neighbour, or -1
    n5: int               # global index of 5' neighbour, or -1
    pos: tuple            # COM (oxDNA units)
    a1: tuple             # base vector (unit)
    a3: tuple             # stacking/helix axis (unit)


def place_frames(mesh, routing):
    """Compute the per-base 3D frames (com, a1, a3) for the scaffold and its WC
    partners. Returns (scaffold_frame, paired_frame, S). Separated from
    build_structure so the duplex GEOMETRY can be unit-tested directly."""
    # global scale: render so geometric edge length ~ bp * RISE  -> vertices ~meet.
    ratios = []
    for e, bp in routing.edge_bp.items():
        L = mesh.edge_length(e)
        if L > 1e-9:
            ratios.append(bp / L)
    ratios.sort()
    scale = ratios[len(ratios) // 2] if ratios else 1.0   # median bp-per-unit-length
    rverts = [_scale(v, RISE * scale) for v in mesh.vertices]

    S = len(routing.scaffold_seq)
    scaffold_frame = [None] * S     # (com, a1, a3) for each scaffold base (5'->3' index)
    paired_frame = [None] * S       # (com, a1, a3) for the WC partner backbone

    # offset the two passes of each undirected edge into two parallel duplexes
    edge_pass = {}
    for seg in routing.segments:
        u, v = seg.arc
        ru, rv = rverts[u], rverts[v]
        axis = _unit(_sub(rv, ru))
        seg_len = _norm(_sub(rv, ru)) or (seg.bp * RISE)
        spacing = seg_len / max(1, seg.bp)
        perp = _any_perp(axis)
        # which pass of this undirected edge is this?
        p = edge_pass.get(seg.edge, 0)
        edge_pass[seg.edge] = p + 1
        side = INTERHELIX * 0.5 * (1 if p == 0 else -1)
        base0 = _add(ru, _scale(perp, side))
        # radial start, decoupled from the interhelix-offset direction
        radial0 = _unit(_cross(axis, perp))
        for k in range(seg.bp):
            g = seg.scaffold_start + k
            if g >= S:
                break
            centre = _add(base0, _scale(axis, (k + 0.5) * spacing))
            radial = _rotate(radial0, axis, k * TWIST)          # outward, rotating
            # oxDNA convention: a1 (base vector) points INWARD toward the pairing
            # partner; the backbone (COM) sits OUTSIDE on +radial. The two strands'
            # backbones end up ~2*BACKBONE_R apart, bases meeting near the axis.
            com = _add(centre, _scale(radial, BACKBONE_R))
            scaffold_frame[g] = (com, _scale(radial, -1.0), axis)
            com_pair = _add(centre, _scale(radial, -BACKBONE_R))
            paired_frame[g] = (com_pair, radial, _scale(axis, -1.0))

    # fill any gap (e.g. unrouted leftover) defensively, with the SAME convention
    for g in range(S):
        if scaffold_frame[g] is None:
            base = (float(g) * RISE, 0.0, 0.0)
            scaffold_frame[g] = (_add(base, (0.0, BACKBONE_R, 0.0)), (0.0, -1.0, 0.0), (1.0, 0.0, 0.0))
            paired_frame[g] = (_add(base, (0.0, -BACKBONE_R, 0.0)), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0))

    return scaffold_frame, paired_frame, S


def build_structure(mesh, routing, staples):
    """Return (nucleotides_in_top_order, box_side).

    nucleotides are ordered EXACTLY as the oxDNA topology lists them (scaffold strand
    first, 3'->5'; then each staple, 3'->5') so .top and .dat stay consistent.
    """
    scaffold_frame, paired_frame, S = place_frames(mesh, routing)

    nucs = []
    # ---- strand 1: scaffold, listed 3'->5' (oxDNA: first listed nt is the 3' end) ----
    seqr = routing.scaffold_seq
    gi = 0
    last = S - 1
    for m, g in enumerate(range(S - 1, -1, -1)):   # 3'->5'
        com, a1, a3 = scaffold_frame[g]
        n3 = gi - 1 if m > 0 else -1
        n5 = gi + 1 if m < last else -1
        nucs.append(Nuc(1, seqr[g], n3, n5, com, _unit(a1), _unit(a3)))
        gi += 1

    # ---- staples ----
    for sid, st in enumerate(staples, start=2):
        n = len(st.seq)
        rev = st.seq[::-1]                      # 3'->5'
        for m, base in enumerate(rev):
            # staple base at 5'->3' index j pairs scaffold position end-1-j
            j = n - 1 - m
            scaf_pos = st.scaffold_end - 1 - j
            if 0 <= scaf_pos < S:
                com, a1, a3 = paired_frame[scaf_pos]
            else:
                com, a1, a3 = ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0), (-1.0, 0.0, 0.0))
            n3 = gi - 1 if m > 0 else -1
            n5 = gi + 1 if m < n - 1 else -1
            nucs.append(Nuc(sid, base, n3, n5, com, _unit(a1), _unit(a3)))
            gi += 1

    # box: cube containing everything + padding
    xs = [p for nuc in nucs for p in nuc.pos]
    span = (max(xs) - min(xs)) if xs else 1.0
    box = span + PAD
    # shift positions to be positive within the box
    mn = min(xs) if xs else 0.0
    shift = -mn + PAD / 2
    for nuc in nucs:
        nuc.pos = (nuc.pos[0] + shift, nuc.pos[1] + shift, nuc.pos[2] + shift)

    return nucs, box


def orthonormal_report(nucs):
    """Sanity metrics: max deviation of |a1|,|a3| from 1 and of a1.a3 from 0."""
    du = dv = 0.0
    for n in nucs:
        du = max(du, abs(_norm(n.a1) - 1), abs(_norm(n.a3) - 1))
        dv = max(dv, abs(_dot(n.a1, n.a3)))
    return {"max_unit_dev": du, "max_orth_dev": dv}


POS_BASE = 0.40   # base/H-bond site distance from COM along a1 (oxDNA-ish)


def duplex_report(mesh, routing):
    """Per-WC-pair geometry sanity: paired BACKBONES (COMs) should sit on the OUTSIDE
    (~2*BACKBONE_R apart) and the BASE sites should nearly meet near the axis
    (~2*(BACKBONE_R-POS_BASE)). Inverting a1 (the bug oxDNA-analysis-tools caught)
    makes backbones collide instead -- this is the guard against that regression."""
    sf, pf, S = place_frames(mesh, routing)
    bb, base = [], []
    for g in range(S):
        if sf[g] is None or pf[g] is None:
            continue
        cs, a1s, _ = sf[g]
        cp, a1p, _ = pf[g]
        bb.append(_norm(_sub(cs, cp)))
        base.append(_norm(_sub(_add(cs, _scale(_unit(a1s), POS_BASE)),
                                _add(cp, _scale(_unit(a1p), POS_BASE)))))
    n = len(bb) or 1
    return {
        "mean_backbone_pair_dist": round(sum(bb) / n, 3),
        "mean_base_pair_dist": round(sum(base) / n, 3),
    }
