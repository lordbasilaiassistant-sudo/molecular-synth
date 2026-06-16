#!/usr/bin/env python3
"""
NORTH-STAR, GEOMETRY-ONLY simulation of positional diamond assembly.

>>> READ THIS FIRST <<<
This script places carbon atoms on a diamond-cubic lattice inside a target box and
writes an .xyz file. It simulates ONLY THE GEOMETRY of a positionally-assembled
diamond. It does NOT simulate the mechanosynthesis CHEMISTRY (positional covalent
bond formation against thermal noise), which is the UNSOLVED part and has NEVER been
experimentally demonstrated (DFT/MD studies only). See docs/north-star.md.

Its real product is the OPERATION BUDGET it prints: the atom counts that show why
single-tooltip positional assembly of even tiny volumes is astronomically slow, i.e.
why this is north-star and not a buildable capability of Molecular Synth v0.

    python northstar/diamond_sim.py --nm 5 --out northstar/out/diamond_5nm.xyz
"""
from __future__ import annotations

import argparse
import os

A_DIAMOND_NM = 0.357  # diamond cubic lattice constant (nm)
# 8 basis atoms per conventional cell (fractional coordinates)
BASIS = [
    (0.0, 0.0, 0.0), (0.0, 0.5, 0.5), (0.5, 0.0, 0.5), (0.5, 0.5, 0.0),
    (0.25, 0.25, 0.25), (0.25, 0.75, 0.75), (0.75, 0.25, 0.75), (0.75, 0.75, 0.25),
]
# carbon number density in diamond, atoms per mm^3
DENSITY_PER_MM3 = 1.76e20


def build_lattice(side_nm: float, a: float = A_DIAMOND_NM):
    n = int(side_nm / a) + 1
    atoms = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                for bx, by, bz in BASIS:
                    x = (i + bx) * a
                    y = (j + by) * a
                    z = (k + bz) * a
                    if x <= side_nm and y <= side_nm and z <= side_nm:
                        atoms.append((x, y, z))
    return atoms


def write_xyz(path, atoms, comment):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"{len(atoms)}\n{comment}\n")
        for x, y, z in atoms:
            # XYZ is conventionally in angstrom; nm -> A = x10
            fh.write(f"C {x*10:.4f} {y*10:.4f} {z*10:.4f}\n")


def human_time(seconds: float) -> str:
    yr = seconds / (365.25 * 24 * 3600)
    if yr >= 1e6:
        return f"{yr/1e6:.1f} million years"
    if yr >= 1:
        return f"{yr:,.0f} years"
    return f"{seconds:,.0f} s"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nm", type=float, default=5.0, help="cube side in nm")
    ap.add_argument("--out", default="northstar/out/diamond.xyz")
    ap.add_argument("--a", type=float, default=A_DIAMOND_NM, help="lattice constant nm")
    ap.add_argument("--tip-rate-hz", type=float, default=1e6,
                    help="optimistic single-tooltip placement rate (Hz)")
    a = ap.parse_args(argv)

    atoms = build_lattice(a.nm, a.a)
    write_xyz(a.out, atoms, f"north-star GEOMETRY-ONLY diamond, {a.nm} nm cube, "
                            f"{len(atoms)} C atoms (chemistry NOT simulated)")

    print("=" * 64)
    print("NORTH-STAR diamond_sim  (GEOMETRY ONLY - chemistry NOT simulated)")
    print("=" * 64)
    print(f"target cube      : {a.nm} nm side")
    print(f"atoms placed     : {len(atoms):,}  -> {a.out}")
    secs_block = len(atoms) / a.tip_rate_hz
    print(f"single-tip time  : {human_time(secs_block)} at {a.tip_rate_hz:.0e} Hz")
    # scale up to macroscopic
    atoms_mm3 = DENSITY_PER_MM3
    secs_mm3 = atoms_mm3 / a.tip_rate_hz
    print(f"\nScale-up reality check (the point of this script):")
    print(f"  1 mm^3 diamond   = {atoms_mm3:.2e} C atoms")
    print(f"  single-tip @ {a.tip_rate_hz:.0e} Hz = {human_time(secs_mm3)}")
    print(f"  -> massive parallelism (or a different approach) is mandatory before")
    print(f"     positional mechanosynthesis is real. This is why it is NORTH-STAR.")
    print(f"\nReminder: positional covalent assembly is UNSOLVED (DFT/MD only, never")
    print(f"demonstrated). The buildable rig makes DNA nanostructures, not this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
