# vision.md — the molecular synthesizer (and what's real *today*)

You want the Orville/Star-Trek synthesizer: describe a thing — and it appears, built with
atomic precision. That is the right north star. This file is the honest map of it, held to
the project rule: **we only keep pushing on the parts that are possible in today's world
with today's cheap materials.**

## The honest truth, in one line

A **universal matter replicator** — arbitrary macroscopic, *functional* objects
materialised from atoms on demand — is **not possible today, at any price.** It needs
positional covalent mechanosynthesis (atom-by-atom assembly of bulk solids), which has
**never been demonstrated** (DFT/simulation only — see [`north-star.md`](north-star.md)).
Anyone who tells you otherwise is selling something.

**But the bottom rung of the dream is real right now.** Programmable, sequence-addressed
**self-assembly** builds *atomically-defined* structures at the nanoscale — today, on a
desk, from orderable parts. That is what this repo compiles and folds: **DNA origami**.
A request (a shape) is **compiled** to a deterministic machine recipe — scaffold route +
optimized staple oligos + the wet-lab protocol + a relaxable 3D structure — and a
sub-$1500 rig folds it. It is a genuine *matter compiler* for one regime: ~10 nm–1 µm,
atomic precision, ~10¹² copies per reaction.

## Why nanoscale is the tractable frontier (measured, not asserted)

The honest reason "atomic precision on a desk" works while "macroscopic matter from
atoms" doesn't is the **physics of scale**. Forces re-sort with size: thermal energy is
scale-free, surface forces scale as L², gravity/weight as L³⁺. So there is a **sweet spot**
— roughly **10 nm to 0.8 µm** — where thermal motion shuffles components together and they
*self-assemble for free*, yet the structure is still large enough to hold a programmed shape
and be imaged. That window is exactly where DNA origami lives. Below it, you can't address a
shape; above it (≳ 0.8 µm) gravity beats thermal motion and self-assembly dies. The path
from molecule to macroscopic is therefore **hierarchical self-assembly** — composing scales,
not inflating a single molecule. See [`../research/FINDINGS.md`](../research/FINDINGS.md)
(exp 2, 5, 10) for the computed crossover scales.

## The thesis we *can* build toward, honestly

> **The molecular synthesizer = a compiler that turns a described structure into a recipe a
> cheap desktop rig executes with atomic precision — and we climb from the demonstrated
> bottom rung (DNA origami) toward molecular manufacturing, one tested step at a time.**

This repo is the bottom rung made concrete:

1. **Compile** — shape → scaffold routing → staple-break **yield optimizer** (Tm balance,
   loop-closure economy, off-target, cross-dimer) → orderable oligos + protocol + 3D.
2. **Fold** — M13 scaffold + staples in Mg²⁺ buffer, a single slow-cool anneal on a
   repurposed Peltier thermocycler.
3. **Verify / harden / functionalise** — a DIY gel confirms the fold; optional sol–gel
   silica hardens it; handle staples position guests (enzymes/catalysts/nanoparticles).

## "If we can figure out DNA, we can figure out this"

Largely true — as a research thesis. DNA is the most programmable matter we have, and the
field is already extending that programmability to *other* matter: DNA as a breadboard for
enzymes/catalysts, DNA-templated synthesis, DNA robots, and artificial molecular
**assemblers** that build defined products by reading a molecular tape. That staircase —
every rung demonstrated in a real lab, honestly labelled by how far up it is — is mapped in
**[the-ladder.md](the-ladder.md)**. We stand on the bottom rungs (fold + harden, on a desk)
and climb one tested step at a time. The top (general molecular manufacturing) stays
north-star until it is demonstrated.

## "Why not CRISPR for molecules — carbon to oxygen?"

Because there's a bright line between **changing the nucleus** (carbon→oxygen is *nuclear*
transmutation — a hard physics wall, north-star) and **changing the bonds** (CO₂→ethanol is
*chemistry* — real, frontier). And the programmable tool isn't a "molecule CRISPR" (general
molecules have no uniform programmable backbone) — it's engineered **enzymes + molecular
assemblers**, which is exactly [the ladder](the-ladder.md) this repo climbs. Full honest
breakdown: **[molecule-vs-element.md](molecule-vs-element.md)**.

## The rule that keeps this real

Every capability we claim must pass the project's gate ([`../validate`](../validate)): the
hardware is **orderable online today and cheap**, and any *capability* we claim is
**demonstrated**. The dream (universal replicator) stays explicitly on the north-star track,
simulated and labelled, until the physics that would unlock it is itself demonstrated. We
build the rungs we can actually stand on — and we keep climbing.
