# /proofs — would it work IRL, given the parts?

The [validate gate](../validate) proves the BOM is **sourceable** and the claims are
**demonstrated in the literature**. This harness goes one step further: it proves the
*specific designs and control this repo emits* are **physically sound given the parts** —
with **evidence (numbers, PASS/FAIL), not assertions.**

```bash
python proofs/run_proofs.py
pip install biopython          # enables the independent-tool Tm proof
```

## What is proven (and how)

| Proof | Method | Evidence |
|---|---|---|
| **Staple addressing** | exact algebra | every emitted oligo is the reverse complement of its scaffold region (it *will* hybridise) and the set tiles the scaffold **exactly once** — no gaps, no overlaps |
| **Thermodynamics** | **independent tool** (Biopython `Tm_NN`, DNA_NN3) | our SantaLucia Tm agrees within ~3 °C — the engine is correct, not just self-consistent |
| **3D structure** | independent re-parse + geometry | the emitted `conf.dat` is a valid oxDNA configuration (15-col rows, orthonormal frames) with B-DNA geometry (backbones outside, bases meeting) — a relaxable structure, not a collapsed clash |
| **Thermocycler control** | **simulation** (firmware PID + lumped thermal model) | the Peltier+PID tracks the 90→20 °C fold ramp to within ~2 °C — the control system executes the protocol |
| **Power budget** | arithmetic from the BOM | worst simultaneous draw (~72 W) fits the 360 W PSU with large margin |
| **Fluidics dosing** | arithmetic from pump rates | target drink/water volumes dispense in seconds-to-minutes |

## The honest line (what a passing proof does and does NOT mean)

- **Does** mean: given the orderable parts, the *math, the design, and the control are
  correct* — the oligos hybridise, the structure is a valid relaxable DNA configuration,
  the thermocycler tracks its ramp, the power and fluidics close. These are the things
  that can be proven away from the bench, and they are proven here.
- **Does NOT** mean: a measured wet-lab **yield**. Whether a *new* shape folds at high
  yield still needs the physical fold + gel (that's [issue #7](../../../issues), the
  make-it-real milestone, and the Mg²⁺×ramp `screen.md` the compiler emits). Simulation
  and independent-tool agreement prove *soundness*, not the final experimental number.

That boundary is the whole discipline: we prove everything that is provable without the
parts, name exactly what still needs the parts, and never blur the two.
