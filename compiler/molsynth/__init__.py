"""
Molecular Synth v0 — compiler.

Turns a target shape (preset / STL / JSON wireframe) into a DNA-origami recipe:
scaffold sequence + optimised staple set + auto-emitted wet-lab protocol, plus
oxDNA/scadnano/IDT exports.

    from molsynth import compile_shape
    summary = compile_shape("tetrahedron", outdir="out/tetra")

CLI:  python -m molsynth compile tetrahedron --out out/tetra
"""

from __future__ import annotations

import os

from . import geometry, scaffold as scaffold_mod, export, protocol as protocol_mod, report as report_mod
from . import decorate as decorate_mod
from . import sequences as sequences_mod
from .staples import build_staples, staple_stats
from .optimizer import YieldModel

__version__ = "0.1.0"
BP_NM = 0.34  # rise per base pair, B-form DNA


def _rotate(s, off):
    off %= len(s)
    return s if off == 0 else s[off:] + s[:off]


def compile_shape(shape, outdir="out", iterations=4000, min_edge_bp=42,
                  scaffold_nM=20, staple_excess=10, mg_mM=12.5, reaction_uL=50,
                  seed=12345, weights_path=None, t_hot=90, t_cold=20, total_min=120,
                  scaffold_offset=0, scaffold_search=1,
                  decorate=0, decorate_end="3p", decorate_spacer="TT", decorate_guests=None,
                  cascade=None, cascade_spacing_nm=10.0):
    """Run the full compile pipeline and write all artifacts to `outdir`.
    Returns a summary dict.

    scaffold_search > 1 searches that many evenly-spaced scaffold START OFFSETS
    (M13mp18 is circular, so the start is a real, free design choice) and keeps the
    offset whose optimized staple set scores best — a genuine yield lever, since
    different M13 regions have different GC bias and repeat content.
    """
    os.makedirs(outdir, exist_ok=True)

    mesh = geometry.load_shape(shape)
    seq, sc_name, synthetic = scaffold_mod.load_scaffold()
    model = YieldModel.load(weights_path) if weights_path else YieldModel()
    design_name = os.path.splitext(os.path.basename(str(shape)))[0] or mesh.name

    chosen_offset = scaffold_offset
    if scaffold_search and scaffold_search > 1:
        offsets = [(scaffold_offset + i * len(seq) // scaffold_search) % len(seq)
                   for i in range(scaffold_search)]
        best = None
        for off in offsets:
            r = scaffold_mod.route(mesh, _rotate(seq, off), sc_name, synthetic,
                                   min_edge_bp=min_edge_bp)
            _, hist = build_staples(r, model, iterations=max(500, iterations // 4),
                                    seed=seed, design_name=design_name)
            sc = hist[-1] if hist else float("inf")
            if best is None or sc < best[0]:
                best = (sc, off)
        chosen_offset = best[1]

    full_rot = _rotate(seq, chosen_offset)
    routing = scaffold_mod.route(mesh, full_rot, sc_name, synthetic,
                                 min_edge_bp=min_edge_bp)
    # off-target screen: mark route positions inside a scaffold repeat (M13 has many),
    # so the optimizer splits long repeats across staple break points.
    offt_mask = sequences_mod.repeat_mask(full_rot)[:len(routing.scaffold_seq)]
    staples, history = build_staples(
        routing, model, iterations=iterations, seed=seed, design_name=design_name,
        offtarget_mask=offt_mask,
    )
    decoration_records = []
    if cascade:
        decoration_records = decorate_mod.decorate_cascade(
            staples, routing, mesh, cascade, spacing_nm=cascade_spacing_nm,
            end=decorate_end, spacer=decorate_spacer)
    elif decorate and decorate > 0:
        decoration_records = decorate_mod.decorate(
            staples, routing, decorate, end=decorate_end,
            spacer=decorate_spacer, guests=decorate_guests)
    stats = staple_stats(staples)

    max_edge_bp = max(routing.edge_bp.values()) if routing.edge_bp else 0
    ramp = protocol_mod.anneal_ramp(t_hot=t_hot, t_cold=t_cold, total_min=total_min)

    design = {
        "design_name": design_name,
        "shape": mesh.name,
        "approx_nm": round(max_edge_bp * BP_NM, 1),
        "scaffold_name": routing.scaffold_name,
        "scaffold_len_used": routing.scaffold_len_used,
        "scaffold_total": len(seq),
        "scaffold_offset": chosen_offset,
        "synthetic_scaffold": synthetic,
        "n_staples": stats.get("n_staples", 0),
        "total_staple_bases": stats.get("total_bases_ordered", 0),
        "decorations": len(decoration_records),
        "scaffold_nM": scaffold_nM,
        "staple_excess": staple_excess,
        "mg_mM": mg_mM,
        "reaction_uL": reaction_uL,
        "anneal_ramp": ramp,
        "mesh": mesh.summary(),
        "staple_stats": stats,
        "optimizer_score": round(history[-1], 3) if history else None,
        "optimizer_score_initial": round(history[0], 3) if history else None,
    }

    written = export.write_all(outdir, design, mesh, routing, staples)
    protocol_md = protocol_mod.emit_protocol(design)
    ppath = os.path.join(outdir, "protocol.md")
    with open(ppath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(protocol_md)
    written["protocol.md"] = ppath

    diag_md = report_mod.yield_report(design, staples, history)
    dpath = os.path.join(outdir, "diagnostics.md")
    with open(dpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(diag_md)
    written["diagnostics.md"] = dpath

    screen_md = protocol_mod.emit_screen(design)
    spath = os.path.join(outdir, "screen.md")
    with open(spath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(screen_md)
    written["screen.md"] = spath

    if decoration_records:
        dec_md = decorate_mod.decoration_md(design_name, decoration_records)
        decpath = os.path.join(outdir, "decoration.md")
        with open(decpath, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dec_md)
        written["decoration.md"] = decpath

    summary = dict(design)
    summary["outdir"] = os.path.abspath(outdir)
    summary["files"] = {k: os.path.abspath(v) for k, v in written.items()}
    return summary
