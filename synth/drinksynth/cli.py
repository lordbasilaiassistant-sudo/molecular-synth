"""CLI:  python -m drinksynth make "<request>" [--dry-run | --port COM4]"""
from __future__ import annotations

import argparse
import sys
import time

from .compiler import compile_drink


def _cmd_make(a):
    out = compile_drink(a.request)
    print(out["protocol"])
    print("\n--- machine commands ---")
    for c in out["commands"]:
        print(c)
    if a.dry_run or not a.port:
        if not a.port and not a.dry_run:
            print("\n(no --port; dry listing. add --port COM4 to actually pour)",
                  file=sys.stderr)
        return 0
    try:
        import serial  # type: ignore
    except ImportError:
        raise SystemExit("pip install pyserial to drive the hardware")
    with serial.Serial(a.port, 115200, timeout=10) as ser:
        time.sleep(2)
        for c in out["commands"]:
            cmd = c.split(";")[0].strip()
            ser.write((cmd + "\n").encode())
            print(f"-> {cmd}")
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                print(f"   {line}")
    print("enjoy.")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="drinksynth")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make", help="compile a drink request to a machine recipe")
    m.add_argument("request", help='e.g. "iced oat latte, large, extra shot"')
    m.add_argument("--port", default=None, help="serial port of the Arduino")
    m.add_argument("--dry-run", action="store_true")
    m.set_defaults(func=_cmd_make)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
