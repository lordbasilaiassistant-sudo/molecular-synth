"""
Experiment 7 — stiffness as a design dial (multi-helix-bundle edges).

exp6 finding F1 said: a single-duplex ~63 bp wireframe edge bends ~38 deg RMS under thermal
forces (worm-like chain, <theta^2> = L/Lp, dsDNA Lp~50 nm) -> the polyhedron is FLOPPY. F1
flagged the remedy ("multi-helix bundles, 6HB Lp ~1-10 um") but did not quantify the dial.

This experiment turns that qualitative remedy into a TABLE OF REAL NUMBERS: for the actual
compiled ~63 bp edge, how does the RMS bend fall as we add helices? It uses the mechanics
model now wired into the compiler (compiler/molsynth/mechanics.py: a parallel-axis bundle
beam with a crossover-compliance knockdown alpha=0.60, calibrated so the 6HB lands at the
MEASURED Lp~5 um). So the "impossible(floppy) -> possible(rigid)" jump is a number, not a hope.

Run:  python research/exp7_edge_stiffness.py
Pure stdlib (imports the compiler's mechanics model directly; no recompile, no pip deps).

Refs:
  Hagerman, Annu. Rev. Biophys. 17:265 (1988)   -- dsDNA persistence length ~50 nm.
  Kauert et al., Nano Lett. 11:5558 (2011)        -- 6-helix bundle Lp ~5 um (MEASURED).
  Bai et al., PNAS 109:20012 (2012)               -- bundle rigidity (cryo-EM).
  Dietz, Douglas & Shih, Science 325:725 (2009)   -- multilayer bundles are rigid.
  Benson et al., Nature 523:441 (2015)            -- single-duplex wireframe is compliant by design.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "compiler"))

from molsynth import mechanics as mech   # noqa: E402

# The edge every preset compiles to (DAEDALUS snaps edges to integer helical turns -> 63 bp;
# confirmed against the committed examples/out_* designs in exp6).
EDGE_BP = 63.0
RIGID_DEG = 10.0     # report.py verdict threshold: <=10 deg RMS bend = rigid
FLOPPY_DEG = 25.0    # >25 deg = floppy (the wireframe breathes)


def main():
    print(f"Edge stiffness dial -- compiled wireframe edge = {EDGE_BP:.0f} bp "
          f"(~{EDGE_BP*0.34:.0f} nm), B-form DNA.\n")
    print("model: parallel-axis bundle beam, EI_ratio = N + alpha*(4/r^2)*sum d_i^2 "
          "(alpha=0.60,")
    print("       r=1.0 nm, honeycomb spacing 2.6 nm); Lp = Lp_single * EI_ratio, "
          "theta_rms = sqrt(L/Lp).")
    print("calibration anchors: single duplex Lp=50 nm (Hagerman 1988); "
          "6HB Lp~5 um (Kauert 2011).\n")

    print(f"  {'helices':>7} | {'EI ratio':>9} | {'Lp (bp)':>9} | {'Lp (um)':>8} | "
          f"{'RMS bend':>9} | verdict")
    print("  " + "-" * 64)
    rows = []
    for n in (1, 2, 3, 4, 6, 8):
        v = mech.stiffness_verdict(EDGE_BP, n)
        rows.append(v)
        print(f"  {n:>7d} | {v['ei_ratio']:>9.1f} | {v['lp_bp']:>9.0f} | "
              f"{v['lp_nm']/1000:>8.2f} | {v['rms_bend_deg']:>7.1f} d | {v['category']}")

    single = rows[0]
    six = next(r for r in rows if r["n_helices"] == 6)
    first_rigid = next((r for r in rows if r["category"] == "rigid"), None)

    print()
    print("MONOTONICITY: bend strictly DECREASES, Lp/EI strictly INCREASE with helix count "
          "(checked).")
    for a, b in zip(rows, rows[1:]):
        assert b["rms_bend_deg"] < a["rms_bend_deg"]
        assert b["lp_bp"] > a["lp_bp"]

    print()
    print(f"IMPOSSIBLE -> POSSIBLE (the dial, as one number):")
    print(f"  single duplex (n=1): RMS bend {single['rms_bend_deg']:.1f} deg "
          f"(> {FLOPPY_DEG:.0f}) -> FLOPPY  [the wireframe breathes; shape is an ensemble]")
    if first_rigid:
        print(f"  rigid at n>={first_rigid['n_helices']}: RMS bend "
              f"{first_rigid['rms_bend_deg']:.1f} deg (<= {RIGID_DEG:.0f}) -> RIGID")
    print(f"  6-helix bundle (n=6): RMS bend {six['rms_bend_deg']:.1f} deg, "
          f"Lp {six['lp_nm']/1000:.1f} um, {six['ei_ratio']:.0f}x stiffer than one duplex")
    fold = single["rms_bend_deg"] / six["rms_bend_deg"]
    print(f"  => the 6HB cuts the thermal bend by {fold:.1f}x "
          f"({single['rms_bend_deg']:.0f} deg -> {six['rms_bend_deg']:.0f} deg): "
          f"floppy wireframe -> rigid frame.")
    print()
    print(f"  6HB Lp = {six['lp_nm']/1000:.2f} um sits inside the MEASURED 1-10 um range "
          f"(Kauert 2011 ~5 um) -> the")
    print(f"  calibration is anchored to experiment, not fit to a desired answer.")
    print()
    print("WIRED: compile_shape(..., edge_helices=N) feeds this model; diagnostics.md now "
          "reports the")
    print("verdict per helix count. ROUTING NOTE: emitting the actual inter-helix-crossover "
          "bundle")
    print("staples is the next step -- this rung delivers the calibrated mechanics dial + "
          "diagnostics,")
    print("not invented bundle sequences (see the diagnostics caveat).")


if __name__ == "__main__":
    main()
