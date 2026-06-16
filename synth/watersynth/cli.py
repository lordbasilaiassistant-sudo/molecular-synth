"""CLI:  python -m watersynth make "<request>" [--reservoir | --port COM5 | --dry-run]"""
from __future__ import annotations

import argparse
import sys
import time

from .compiler import compile_water


def _cmd_make(a):
    out = compile_water(a.request, from_reservoir=a.reservoir)
    print(out["protocol"])
    print("\n--- machine commands ---")
    for c in out["commands"]:
        print(c)
    if a.dry_run or not a.port:
        if not a.port and not a.dry_run:
            print("\n(no --port; dry listing. add --port COM5 to actually pour)",
                  file=sys.stderr)
        return 0
    try:
        import serial  # type: ignore
    except ImportError:
        raise SystemExit("pip install pyserial to drive the hardware")
    with serial.Serial(a.port, 115200, timeout=600) as ser:
        time.sleep(2)
        for c in out["commands"]:
            cmd = c.split(";")[0].strip()
            ser.write((cmd + "\n").encode())
            print(f"-> {cmd}")
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                print(f"   {line}")
    print("here's your water.")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="watersynth")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="compile a water request to a machine recipe")
    m.add_argument("request", help='e.g. "large glass of cold water"')
    m.add_argument("--reservoir", action="store_true",
                   help="dispense from a pre-filled tank instead of harvesting from air")
    m.add_argument("--port", default=None, help="serial port of the Arduino")
    m.add_argument("--dry-run", action="store_true")
    m.set_defaults(func=_cmd_make)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
