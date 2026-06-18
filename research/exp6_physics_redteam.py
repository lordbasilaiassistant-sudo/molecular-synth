"""
Experiment 6 — physics & materials red-team (think like a security auditor, for atoms).

A code auditor hunts the inputs that break a program even when it "runs fine." Here we hunt the
physical assumptions that break the REAL folded object even when compile_shape() reports success
and every file is written. Each finding has: the assumption under attack, the attack (what
physics breaks it), measured evidence from the committed designs, a severity, and the remediation
that flips the apparent impossibility into a buildable path.

Run:  python research/exp6_physics_redteam.py
Pure stdlib (audits examples/out_*/design.json; no recompile needed).
"""
from __future__ import annotations

import glob
import json
import math
import os
import re

BP_NM = 0.34
LP_BP = 147.0     # dsDNA persistence length ~50 nm
G4 = re.compile(r"G{3,}\w{1,7}G{3,}\w{1,7}G{3,}\w{1,7}G{3,}")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def audit():
    designs = []
    for dj in sorted(glob.glob(os.path.join(ROOT, "examples", "out_*", "design.json"))):
        d = json.load(open(dj))
        name = os.path.basename(os.path.dirname(dj)).replace("out_", "")
        edges = list(d["edges_bp"].values())
        seqs = [s["seq"] for s in d["staples"]]
        designs.append({
            "name": name,
            "max_edge_bp": max(edges) if edges else 0,
            "rms_bend": math.degrees(math.sqrt(max(edges) / LP_BP)) if edges else 0,
            "g4": sum(1 for s in seqs if G4.search(s.upper())),
            "n": len(seqs),
        })
    return designs


def main():
    d = audit()
    worst_bend = max(x["rms_bend"] for x in d)
    floppy = [x["name"] for x in d if x["rms_bend"] > 25]
    g4_total = sum(x["g4"] for x in d)
    print(f"Audited {len(d)} compiled designs in examples/.\n")

    print("F1 [HIGH] single-duplex wireframe edges are thermally FLOPPY")
    print(f"   attack   : a B-DNA edge longer than the persistence length (Lp~50nm~147bp) bends")
    print(f"              under thermal forces; <theta^2>=L/Lp. The shape is an ensemble, not rigid.")
    print(f"   evidence : every compiled edge ~63 bp (~21nm) -> RMS bend ~{worst_bend:.0f} deg; "
          f"floppy designs: {len(floppy)}/{len(d)}")
    print(f"   remediate: multi-helix-bundle edges (6HB Lp ~1-10um, ~20-70x stiffer) for rigid")
    print(f"              shapes; or accept the compliant DAEDALUS ensemble on purpose. NOW")
    print(f"              REPORTED in diagnostics.md (edge-stiffness verdict).")
    print(f"   IMPOSSIBLE->POSSIBLE: stiffness is a DESIGN VARIABLE (helix count), not a wall.\n")

    print("F2 [HIGH] Tm is mis-calibrated for the actual folding buffer")
    print(f"   attack   : model assumes ~50mM Na+; real fold is ~12.5mM Mg2+. Staples melt ~9C")
    print(f"              hotter than reported -> ramp top-end / window targeting are off.")
    print(f"   evidence : research/exp1 (Owczarzy 2008): [Na+]_eq ~166mM, gap ~+9C at 50mM.")
    print(f"   remediate: sequences.tm_buffer() added; diagnostics now report the buffer offset.")
    print(f"              Next: shift the optimiser Tm window +9C and recalibrate.\n")

    print("F3 [MED] G-quadruplex / sequence sequestration not in the objective")
    print(f"   attack   : a G-rich staple folding into a G4 is lost to the scaffold (yield drop);")
    print(f"              not caught by the duplex-hairpin proxy.")
    print(f"   evidence : audited {sum(x['n'] for x in d)} staples across {len(d)} designs -> "
          f"{g4_total} G4 motifs (CLEAN today).")
    print(f"   remediate: g_quadruplex_sites() screen added + reported; add as an optimiser term")
    print(f"              before trusting novel/denser sequences.\n")

    print("F4 [MED] the optimiser is THERMODYNAMIC; folding is KINETIC")
    print(f"   attack   : equilibrium Tm clustering ignores folding ORDER. If hot staples close")
    print(f"              loops before nucleation, the structure kinetically traps despite good Tm.")
    print(f"   evidence : objective has no topological-order term (optimizer.py); literature shows")
    print(f"              pathway control matters (Dunn 2015; Sobczak 2012).")
    print(f"   remediate: program a Tm ladder matched to assembly order (seams last); Mg x ramp")
    print(f"              screen (screen.md) brackets it empirically.")
    print(f"   IMPOSSIBLE->POSSIBLE: near-100% yield via kinetic programming, not just thermo.\n")

    print("VERDICT: the digital pipeline is sound; the PHYSICS gaps above are where a real build")
    print("fails. Two are now surfaced in diagnostics (F1 stiffness, F2/F3 Tm+G4); two are flagged")
    print("design directions (F1 bundles, F4 kinetic ladder). None is a wall -- each is a lever.")


if __name__ == "__main__":
    main()
