# ROADMAP

The goal is the [molecular synthesizer](docs/vision.md): *describe a structure → a compiler
turns it into a recipe a cheap desktop rig executes with atomic precision.* We add depth only
where **today + cheap materials** allow, and we keep the universal-replicator dream honestly
on the [north-star](docs/north-star.md) track.

## Now (v0 — shipped)
- Molecular Synth compiler: shape → scaffold + optimized staples + protocol + **3D oxDNA
  structure** + yield diagnostic; pure-stdlib core; STL/PLY/JSON input.
- < $1500 rig blueprint (Peltier thermocycler, DIY gel, optional STM) + firmware + CAD.
- Validate gate (sourceable AND demonstrated); citation-backed `science.md`.

## Research & diagnostics (shipped this cycle)
- **Measured molecular study** ([research/FINDINGS.md](research/FINDINGS.md)) — reproducible
  experiments: the Tm model validated against Biopython (mean |ΔT| = 0.86 °C); a folding-buffer
  salt calibration (the 50 mM default runs ~9 °C cold for the real 12.5 mM Mg²⁺ fold; na_eq ≈
  166 mM); the physics of scale (the manipulation/self-assembly sweet spot is ~10 nm–0.8 µm =
  the origami window); the compiler's design levers (scaffold offset ≈ 3× proxy lever;
  GC-uniformity predicts the Tm-spread floor at r = +0.73); and an adversarial physics red-team.
- **Reality-check diagnostics.** Every `diagnostics.md` now carries a "Physics & materials
  reality check": edge-stiffness verdict (worm-like chain), G-quadruplex audit, buffer-accurate
  Tm, and the thermodynamic-vs-kinetic caveat — so diagnostics never overclaim the real fold.
- **Physics-backed compiler upgrades (shipped):** a **stiffness dial** (`edge_helices`:
  single-duplex → multi-helix bundle, 6HB Lp ~1–10 µm — reported verdict; bundle routing is the
  next step); a **buffer-Tm recalibration** (optimiser + diagnostics now score at the real
  12.5 mM Mg²⁺ salt, window shifted to [59,73] °C); an opt-in **kinetic Tm-ladder** term
  (programs folding *order*, default off; Dunn 2015); and a **hierarchy simulation** (origami →
  super-lattice; self-assembly ceiling at the 0.79 µm crossover).

## Next (physics-backed, queued)
- **Bundle routing** — actually emit the multi-duplex scaffold + inter-helix crossovers so the
  stiffness dial changes the *design*, not only the verdict.
- **GC-uniformity offset ranking** — rank scaffold offsets by GC-uniformity of the routed region
  (the measured r = +0.73 lever) to lower the cooperative-annealing Tm-spread floor.

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

## Never (north-star, not roadmap)
Universal matter replication / diamondoid mechanosynthesis stays simulated and labelled
until the underlying chemistry is itself demonstrated. We build the rungs we can stand on.
