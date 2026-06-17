"""CLI:  python -m printsynth plan <model.stl> [--material PLA] [--infill 0.2] [--layer 0.2]"""
from __future__ import annotations

import argparse

from .compiler import compile_print


def _cmd_plan(a):
    job = compile_print(stl=a.stl, material=a.material, infill=a.infill, layer_mm=a.layer)
    print(job["protocol"])
    print("\n--- machine commands ---")
    print("  " + " | ".join(job["commands"]))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="printsynth", description="3D-print maker: mesh -> print job")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("plan", help="estimate + emit a print job for an STL")
    c.add_argument("stl")
    c.add_argument("--material", default="PLA")
    c.add_argument("--infill", type=float, default=0.20)
    c.add_argument("--layer", type=float, default=0.20)
    c.set_defaults(func=_cmd_plan)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
