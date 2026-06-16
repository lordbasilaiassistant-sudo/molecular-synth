#!/usr/bin/env python3
"""
Stream a compiled anneal ramp to the thermocycler firmware over serial.

The compiler writes the ramp into <outdir>/design.json (key "anneal_ramp": list of
[tempC, minutes]). This host script reads it and sends one STEP command per row,
so the physical block runs exactly the ramp the protocol printed.

    pip install pyserial
    python host_ramp.py --design ../../examples/out_cube/design.json --port COM3

With --dry-run it prints the commands without needing the hardware (useful to check
the wiring of software -> protocol -> firmware).
"""
from __future__ import annotations

import argparse
import json
import sys
import time


def load_ramp(design_path):
    with open(design_path, "r", encoding="utf-8") as fh:
        d = json.load(fh)
    meta = d.get("meta", d)
    ramp = meta.get("anneal_ramp")
    if not ramp:
        raise SystemExit("no anneal_ramp in design.json")
    return ramp


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True, help="path to compiled design.json")
    ap.add_argument("--port", default=None, help="serial port, e.g. COM3 or /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    ramp = load_ramp(a.design)
    total_min = sum(m for _, m in ramp)
    print(f"[host] {len(ramp)} steps, ~{total_min/60:.1f} h total")

    if a.dry_run or not a.port:
        for t, m in ramp:
            print(f"STEP {t} {int(m*60)}")
        if a.dry_run:
            return 0
        print("[host] no --port given; dry listing only", file=sys.stderr)
        return 0

    try:
        import serial  # type: ignore
    except ImportError:
        raise SystemExit("pip install pyserial to drive the hardware")

    with serial.Serial(a.port, a.baud, timeout=5) as ser:
        time.sleep(2)  # board reset
        for t, m in ramp:
            cmd = f"STEP {t} {int(m*60)}\n"
            ser.write(cmd.encode())
            print(f"[host] -> {cmd.strip()}")
            # wait for DONE
            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    print(f"[fw]  {line}")
                if line == "DONE":
                    break
        ser.write(b"STOP\n")
    print("[host] ramp complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
