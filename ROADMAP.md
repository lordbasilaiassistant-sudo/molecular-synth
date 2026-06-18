# ROADMAP

The goal is the [synthesizer thesis](docs/vision.md): *ask for X → an AI request-compiler
routes it to the right cheap desktop maker.* We add makers and depth only where **today +
cheap materials** allow, and we keep the universal-replicator dream honestly on the
[north-star](docs/north-star.md) track.

## Now (v0 — shipped)
- Molecular Synth compiler: shape → scaffold + optimized staples + protocol + **3D oxDNA
  structure** + yield diagnostic; pure-stdlib core; STL/PLY/JSON input.
- < $1500 rig blueprint (Peltier thermocycler, DIY gel, optional STM) + firmware + CAD.
- Validate gate (sourceable AND demonstrated); citation-backed `science.md`.
- Drink Synth: the buildable-today macroscale instance ("iced oat latte" → machine recipe).
- Water Synth: "a glass of drinkable water on demand" via atmospheric water generation
  (Peltier condensation + carbon filter + UV-C). The most tractable maker, humanity-useful.

## Federation & research (shipped this cycle)
- **One front door.** `synth/itemsynth` is now a registry-driven spine (`makers.py` = a single
  source of truth per maker: keywords + compiler + output adapter) and orchestrates the Maker
  Catalog as an engine — `synthesize()` routes one ask to a maker, north-stars the impossible,
  or falls back to the catalog for cross-maker / cataloged requests (`feasibility()`, `plan()`).
- **Measured molecular study** ([research/FINDINGS.md](research/FINDINGS.md)) — reproducible
  experiments: the Tm model validated against Biopython (mean |ΔT| = 0.86 °C); a folding-buffer
  salt calibration (the 50 mM default runs ~9 °C cold for the real 12.5 mM Mg²⁺ fold; na_eq ≈
  166 mM); the physics of scale (the manipulation/self-assembly sweet spot is ~10 nm–0.8 µm =
  the origami window); the compiler's design levers (scaffold offset ≈ 3× proxy lever;
  GC-uniformity predicts the Tm-spread floor at r = +0.73); and an adversarial physics red-team.
- **Reality-check diagnostics.** Every `diagnostics.md` now carries a "Physics & materials
  reality check": edge-stiffness verdict (worm-like chain), G-quadruplex audit, buffer-accurate
  Tm, and the thermodynamic-vs-kinetic caveat — so diagnostics never overclaim the real fold.

## Active: physics-backed compiler upgrades (in progress, not yet merged)
Driven by the red-team findings; each must land tested + measured before it ships:
- **Stiffness as a dial** — multi-helix-bundle edges (6HB Lp ~1–10 µm) so the compiler can emit
  *rigid* large shapes, not only compliant single-duplex wireframes (red-team F1).
- **Buffer Tm recalibration + GC-uniformity offset ranking** — shift the optimiser Tm window to
  the real-buffer scale and rank scaffold offsets by GC-uniformity (the r = +0.73 lever).
- **Kinetic Tm-ladder** — an opt-in objective term that programs folding *order*, not just
  equilibrium Tm (red-team F4; Dunn 2015).
- **Hierarchy simulation** — origami unit cells → super-lattice, measuring where the assembly's
  own physics crossovers land (the literal next step of "compose the scales" toward macroscopic).

## Climbing the ladder ([docs/the-ladder.md](docs/the-ladder.md))
- **Rung 0–1** (fold + harden): shipped, on a desk.
- **Rung 2** (DNA as a breadboard): ✅ `--decorate` emits functional handle staples that
  position a guest (enzyme/catalyst/nanoparticle) at a chosen site, with the anti-handle
  map. Next rungs (3 DNA-templated synthesis, 4 robots, 5 assemblers) stay lab-frontier.

## Next (open issues → fabrication-grade)
Tracked in [Issues](https://github.com/lordbasilaiassistant-sudo/molecular-synth/issues):
- **#1** Face-respecting A-trail routing (production-grade scaffold paths). ✅ the router
  now searches (seeded multi-restart) for the routing with the fewest *true* vertex
  crossings — turns to a non-adjacent edge in the planar rotation — reaching **1–2
  crossings** on every Platonic preset (icosahedron 23→1, octahedron 8→2, ≥96%
  adjacent-turn), close to PERDIX/DAEDALUS, with the single-scaffold-circuit invariant
  still machine-checked.
- **#2** oxDNA relaxation inputs + reduce vertex-junction stretch. ✅ relax inputs emitted.
- **#3** caDNAno JSON export (standard-tool interop).
- **#4** ML-trained yield model (experimental) over the heuristic baseline.
- **#5** PLY input (DAEDALUS/PERDIX interop) + STL robustness. ✅ PLY landed.
- **#6** Tighten staple Tm uniformity.
- **#9** Auto-emit the Mg²⁺ × ramp screen. ✅ screen emitted.
- **#10** Contributor docs + templates + this roadmap. ✅

## Make-it-real milestone
- **#7** Wet-lab validation: fold a known published design on the rig, confirm the gel band,
  then trust novel compiled designs. This is the moment the blueprint becomes a result.

## New maker domains (extend the thesis)
- **#8** 3D-print maker — ✅ **shipped** (`synth/printsynth`): STL → print job (material,
  settings, filament/time/cost estimate, slicer hand-off). Physical objects join the
  catalog of what the synth makes.
- Future: automated kitchen, PCB mill — each must pass the gate (cheap, orderable,
  demonstrated) before it ships.

## Never (north-star, not roadmap)
Universal matter replication / diamondoid mechanosynthesis stays simulated and labelled
until the underlying chemistry is itself demonstrated. We build the rungs we can stand on.
