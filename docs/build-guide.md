# BUILD GUIDE — from an empty bench to a folded nanostructure

This is the full blueprint: order → build the rig → install the software → **validate
the rig on a known design** → fold your own compiled design → verify → (optionally)
harden to silica. Everything uses parts orderable online today; the rig is < $1500
([`../bom/bom.md`](../bom/bom.md)).

> **What you will actually make:** a DNA-origami nanostructure, ~10–100 nm, in ~10¹²
> copies per reaction, verified as a folded band on a gel and (optionally) converted to
> rigid silica. **Not** a macroscopic object, **not** diamondoid — see
> [`science.md`](science.md) / [`north-star.md`](north-star.md). This is the real,
> demonstrated first rung; the guide keeps you on it.

**Total to first verified fold:** ≈ $623 rig (one-time) + ≈ $540 consumables
(first design, oPool path) ≈ **$1.16k all-in**, then ≈ $205 per additional design.
Calendar time ≈ **2–4 weeks** (mostly oligo + scaffold shipping), **~2 active days**
of bench work.

---

## Phase 0 — Decide & order (Day 0; then wait on shipping)

1. **Order the rig hardware** ([`bom.json`](../bom/bom.json), category `rig-hardware`,
   ≈ $623): Peltier + BTS7960 H-bridge + Arduino + thermistor + aluminium block + 12 V
   PSU + heatsink (thermocycler ≈ $108); IVYX gel system + blue transilluminator
   (≈ $290); vortex + mini-centrifuge (≈ $135); micropipette set (≈ $90).
2. **Order consumables** (category `consumable`, ≈ $540 first design): M13mp18 scaffold
   (NEB N4040, $40); **a published, known-good staple set as an oPool** (see Phase 4) —
   this is your rig-validation reagent; MgCl₂, 50× TAE, agarose, GelGreen, DNA ladder,
   PEG-8000, PCR tubes, nuclease-free water (reusable kit ≈ $330).
3. While you wait: build the rig (Phases 1–2) and install the software (Phase 3).

> **Sourcing reality:** IDT and NEB sell to individuals with a credit card and ship to
> residential addresses; origami oligos (32–42 nt) are far below any gene-synthesis
> screening threshold. Nothing here needs an institutional account.

---

## Phase 1 — Build the folding thermocycler (~½ day)

Stack: CPU heatsink+fan → Peltier (TEC1-12706) → drilled aluminium block (0.2 mL tube
bores) → printed insulating collar ([`../hardware/cad/thermocycler_block.scad`](../hardware/cad/thermocycler_block.scad)).
Thermal-paste each interface. Hold the thermistor in the block (collar channel).

Wiring (see [`../hardware/README.md`](../hardware/README.md)):
```
12V 30A PSU ─┬─► BTS7960 H-bridge ─► Peltier   (reversible: heat AND cool)
             └─► CPU fan (always on)
Arduino Uno:  D9→H-bridge PWM(EN)   D7/D8→direction(heat/cool)   D5→fan
              A0→100k NTC thermistor (4.7k pull-up to 5V)
```
Flash [`../hardware/firmware/thermocycler.ino`](../hardware/firmware/thermocycler.ino)
(Arduino IDE → Uno → Upload). **Bench test before any DNA:** open the serial monitor
@115200, send `SET 60`, confirm the block reaches ~60 °C and holds; send `SET 90`
then watch it cool to `SET 20` — the H-bridge must actively cool, not just coast. The
firmware has a hard 99 °C cutoff. *No-electronics alternative:* a sous-vide bath +
manual setpoint steps.

---

## Phase 2 — Build the gel verification rig (~1–2 hr)

Easiest: the IVYX all-in-one (tank + integrated 50/100 V supply). DIY alternative:
print [`../hardware/cad/gel_box.scad`](../hardware/cad/gel_box.scad), add stainless/Pt
wire electrodes, and supply 60–90 V. **Critical:** origami gels need **Mg²⁺ in the gel
and running buffer** (1× TAE + ~11 mM MgCl₂) and must run **cold** (on ice), or the
origami unfolds. A 0–30 V bench supply is **not** enough — use 50–100 V.

---

## Phase 3 — Install the software & compile a design (~15 min)

```bash
cd compiler
python -m molsynth compile tetrahedron --out out/tetra      # pure stdlib, no installs
# optional extras (real M13 fetch, scadnano export, STL):
pip install -r requirements.txt
python -m molsynth fetch-scaffold
```
Outputs in `out/tetra/`: `staples.csv` (+ `staples_idt_plate.txt` / `staples_opool.txt`
to order), `protocol.md` (the recipe), `diagnostics.md` (predicted yield), and the 3D
structure `conf.dat`/`structure.pdb` — open `conf.dat` in
[oxView](https://sulcgroup.github.io/oxdna-viewer/) to *see* the design and relax it in
[oxDNA](https://lorenzo-rovigatti.github.io/oxDNA/) before spending money.

---

## Phase 4 — VALIDATE THE RIG on a known design FIRST (do not skip)

Before trusting any novel compiled design, prove the **rig** works with a
**published, known-to-fold** structure. Recommended: the **Rothemund rectangle** or a
**published wireframe tetrahedron** (DAEDALUS/PERDIX) whose staple set is in the paper's
supplement. Order that exact staple set (as an oPool) + the matching scaffold, fold it
per Phase 5, and confirm a clean gel band (Phase 6). This separates *rig faults* from
*design faults* — the single most important discipline for making this real. Only once
the rig reproduces a published design do you trust your own compiled outputs.

---

## Phase 5 — Fold (one anneal, ~2–20 h)

Follow the auto-emitted `protocol.md` for your design. In short: mix scaffold (~20 nM)
+ staples (5–10× each) in 1× TAE + 12.5 mM MgCl₂ (≈50 µL in a PCR tube); run the anneal
ramp on the thermocycler:
```bash
python ../hardware/firmware/host_ramp.py --design out/tetra/design.json --port COM3
```
Heat ~90 °C → slow-cool ~20 °C. Simple 2D folds in ~2 h; stiff 3D wants a longer ramp
and a per-design Mg²⁺ × ramp screen (the protocol lists the screen grid).

---

## Phase 6 — Verify on the gel (~2–3 h, cold)

Cast 1.5–2 % agarose in 1× TAE + ~11 mM MgCl₂. Load: (a) your folded sample, (b) a
**scaffold-only control**, (c) a **ladder**. Run 60–90 V on ice, stain GelGreen, image
on the blue transilluminator. **Read-out:** a well-folded origami is one **tight band**
that migrates *differently from the scaffold-only lane*; smear / well-stuck material =
aggregation/misfolding → slow the ramp or retune Mg²⁺. (Gel tells folded-vs-not, not nm
shape — shape confirmation needs AFM/TEM, out of the desktop budget.)

---

## Phase 7 — (Optional) Purify & harden to silica

- **Purify:** PEG-8000 precipitation (15 % PEG / 500 mM NaCl / Mg²⁺), spin in the
  mini-centrifuge, resuspend — removes excess staples (Stahl 2014).
- **Harden (fume hood):** incubate purified origami with an aminosilane (TMAPS/APTES)
  then TEOS in the Mg²⁺ buffer, days at RT → a rigid **silica replica** (Liu 2018). This
  is the step that turns the soft template into a durable, dryable, imageable object.
  TEOS/methanol are flammable — ventilate.

---

## Phase 8 — (Optional) Atomic-resolution demo (STM)

Build the DIY STM ([`../hardware/cad/stm_mount.scad`](../hardware/cad/stm_mount.scad))
and resolve the **HOPG graphite atomic lattice** — proof that single-atom imaging is a
desktop-cheap reality. Honest note: this images graphite atoms, **not** your origami
(that needs AFM/cryo-TEM). It's the "atomic resolution is real" trophy, decoupled from
product QC.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No band / everything in the well | aggregation; Mg²⁺ too high or ramp too fast | lower Mg²⁺ (try 8–12.5 mM), slow the ramp |
| Only a fast diffuse front | only staples; scaffold didn't fold | check scaffold conc/quality; verify staple:scaffold ratio |
| Band same as scaffold-only | no folding | confirm staples present & correct scaffold (p7249 vs p8064) |
| Block won't cool | H-bridge wired one-way | confirm D7/D8 direction pins; the Peltier must reverse |
| Smeary/streaky gel | gel warmed up | run colder / lower voltage; Mg²⁺ in the running buffer |

## Safety
Flammable silane/alcohol → fume hood. GelGreen (not EtBr). Gel runs at 60–90 V — fuse
and insulate. 12 V/30 A Peltier supply — appropriate gauge wire. Follow local rules.

## What "reality" means here
You will have **manufactured atomically-defined, sequence-addressed matter at the
nanoscale on a desk for ~$1k**, designed by your own one-command compiler, verified by
gel, optionally hardened to silica. That is real, demonstrated nanofabrication. It is
the first rung — not the macroscopic matter compiler. The ambition stays honestly on the
[north-star track](north-star.md) until the chemistry that would extend it is itself
demonstrated.
