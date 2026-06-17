"""Command-line interface:  python -m molsynth <command>"""

from __future__ import annotations

import argparse
import json
import sys

from . import compile_shape, geometry
from . import scaffold as scaffold_mod


def _cmd_compile(a):
    guests = [g.strip() for g in a.decorate_guests.split(",")] if a.decorate_guests else None
    cascade = [g.strip() for g in a.cascade.split(",")] if a.cascade else None
    summary = compile_shape(
        a.shape, outdir=a.out, iterations=a.iterations, min_edge_bp=a.min_edge_bp,
        scaffold_nM=a.scaffold_nM, staple_excess=a.excess, mg_mM=a.mg,
        reaction_uL=a.volume, seed=a.seed, weights_path=a.weights,
        t_hot=a.t_hot, t_cold=a.t_cold, total_min=a.anneal_min,
        scaffold_search=a.scaffold_search, scaffold_offset=a.scaffold_offset,
        decorate=a.decorate, decorate_end=a.decorate_end,
        decorate_spacer=a.decorate_spacer, decorate_guests=guests,
        cascade=cascade, cascade_spacing_nm=a.cascade_spacing_nm,
    )
    st = summary["staple_stats"]
    print(f"[molsynth] compiled '{summary['shape']}' -> {summary['outdir']}")
    print(f"  scaffold : {summary['scaffold_name']} "
          f"({summary['scaffold_len_used']} nt used"
          f"{', SYNTHETIC fallback' if summary['synthetic_scaffold'] else ''})")
    print(f"  staples  : {st['n_staples']} oligos, "
          f"{st['n_crossover_staples']} crossover, "
          f"len {st['len_min']}-{st['len_max']} (mean {st['len_mean']})")
    print(f"  Tm       : mean {st['tm_mean_C']} °C, spread (stdev) {st['tm_stdev_C']} °C")
    print(f"  optimizer: score {summary['optimizer_score_initial']} -> "
          f"{summary['optimizer_score']}")
    print(f"  est. size: ~{summary['approx_nm']} nm (longest edge)")
    if summary.get("decorations"):
        print(f"  decorate : {summary['decorations']} handle site(s) -> decoration.md")
    print("  files    :")
    for k, v in summary["files"].items():
        print(f"    - {k}")
    if a.json:
        print(json.dumps({k: summary[k] for k in
                          ("design_name", "shape", "n_staples", "approx_nm",
                           "synthetic_scaffold", "optimizer_score")}, indent=2))
    return 0


def _cmd_fetch(a):
    try:
        seq = scaffold_mod.fetch_m13(a.accession)
        print(f"[molsynth] fetched M13mp18 ({len(seq)} nt) -> "
              f"{scaffold_mod.M13_PATH}")
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"[molsynth] fetch failed: {e}", file=sys.stderr)
        print("  The compiler still runs on the deterministic synthetic scaffold.",
              file=sys.stderr)
        return 1


def _cmd_info(a):
    mesh = geometry.load_shape(a.shape)
    print(json.dumps(mesh.summary(), indent=2))
    return 0


def _cmd_validate(a):
    # Defer to the repo-level gate so there is a single source of truth.
    import importlib.util
    import os
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    vpath = os.path.join(here, "validate", "validate.py")
    if not os.path.exists(vpath):
        print(f"validate.py not found at {vpath}", file=sys.stderr)
        return 2
    spec = importlib.util.spec_from_file_location("molsynth_validate", vpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.main([])


def build_parser():
    p = argparse.ArgumentParser(prog="molsynth",
                                description="Molecular Synth v0 — shape -> DNA origami recipe")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compile", help="compile a shape into a DNA origami recipe")
    c.add_argument("shape", help="preset (tetrahedron/cube/octahedron/square), .stl, or .json")
    c.add_argument("--out", default="out", help="output directory")
    c.add_argument("--iterations", type=int, default=4000, help="optimizer iterations")
    c.add_argument("--min-edge-bp", type=int, default=42, dest="min_edge_bp")
    c.add_argument("--scaffold-nM", type=float, default=20, dest="scaffold_nM")
    c.add_argument("--excess", type=float, default=10, help="staple molar excess")
    c.add_argument("--mg", type=float, default=12.5, help="MgCl2 mM")
    c.add_argument("--volume", type=float, default=50, help="reaction uL")
    c.add_argument("--seed", type=int, default=12345)
    c.add_argument("--weights", default=None, help="JSON file of learned YieldModel weights")
    c.add_argument("--t-hot", type=float, default=90, dest="t_hot")
    c.add_argument("--t-cold", type=float, default=20, dest="t_cold")
    c.add_argument("--anneal-min", type=float, default=120, dest="anneal_min")
    c.add_argument("--scaffold-search", type=int, default=8, dest="scaffold_search",
                   help="search N scaffold start offsets, keep the best-scoring (yield lever; "
                        "halves the objective + tightens Tm). Use 1 to disable.")
    c.add_argument("--scaffold-offset", type=int, default=0, dest="scaffold_offset")
    c.add_argument("--decorate", type=int, default=0,
                   help="rung 2: add N functional handle sites (DNA breadboard) -> decoration.md")
    c.add_argument("--decorate-end", default="3p", choices=["3p", "5p"], dest="decorate_end")
    c.add_argument("--decorate-spacer", default="TT", dest="decorate_spacer")
    c.add_argument("--decorate-guests", default=None, dest="decorate_guests",
                   help="comma-separated guest labels for the handle sites")
    c.add_argument("--cascade", default=None,
                   help="ordered enzyme cascade, comma-separated (e.g. 'GOx,HRP'); places "
                        "sites at --cascade-spacing-nm apart")
    c.add_argument("--cascade-spacing-nm", type=float, default=10.0, dest="cascade_spacing_nm",
                   help="target inter-enzyme spacing in nm for --cascade")
    c.add_argument("--json", action="store_true", help="also print a JSON summary")
    c.set_defaults(func=_cmd_compile)

    f = sub.add_parser("fetch-scaffold", help="download real M13mp18 scaffold from NCBI")
    f.add_argument("--accession", default="V00604.2")
    f.set_defaults(func=_cmd_fetch)

    i = sub.add_parser("info", help="print the wireframe summary of a shape")
    i.add_argument("shape")
    i.set_defaults(func=_cmd_info)

    v = sub.add_parser("validate", help="run the sourceable+demonstrated gate")
    v.set_defaults(func=_cmd_validate)
    return p


def main(argv=None):
    p = build_parser()
    a = p.parse_args(argv)
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
