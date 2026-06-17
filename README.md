# Molecular Synth v0

**A desktop rig + AI compiler that programmably manufactures atomically-precise 3D
nanostructures by DNA self-assembly — built entirely from parts you can order online
or repurpose from non-lab gear.**

You describe a shape; the compiler emits the DNA scaffold + staple sequences to order
and the step-by-step wet-lab recipe; a ~$623 rig (repurposed Peltier thermocycler +
DIY gel) folds it and checks it; an optional sol–gel step hardens the DNA into rigid
silica.

> ### Honest scope (read this)
> **The output is a DNA-self-assembled nanostructure (~10 nm – ~1 µm), optionally
> hardened to silica/metal — NOT a macroscopic object, and NOT Drexler diamondoid
> mechanosynthesis.** Every capability claimed on the buildable track cites a real,
> experimentally-demonstrated paper ([`docs/science.md`](docs/science.md),
> [`docs/claims.json`](docs/claims.json)). The bigger ambition (positional covalent
> assembly, macroscopic atomically-precise manufacturing) is real-as-a-goal but
> **not yet demonstrated**, so it lives, clearly labelled and simulated-only, on the
> [north-star track](docs/north-star.md) and is never costed into the BOM.

This is genuine, demonstrated bottom-up nanofabrication — the real first rung of the
ladder — described without overclaiming the rungs above it.

> 🧪 **The bigger picture — the "synthesizer" (ask for anything, a machine makes it):**
> a universal matter replicator (materialising matter from energy) is north-star — not
> possible today, any price. But the *spirit* — "ask, and it appears" — is partly real
> now as a **federation of cheap desktop makers + an AI request-compiler**. This repo
> holds three instances: **Molecular Synth** (atomic precision, nanoscale, the deep-tech
> flagship), **[Water Synth](synth/)** (a glass of drinkable water harvested from air —
> the most tractable one, and humanity-useful), and **[Drink Synth](synth/)** ("iced oat
> latte" → machine recipe). See [`docs/vision.md`](docs/vision.md).

> 🔧 **Building it for real? Start with the [BUILD GUIDE](docs/build-guide.md)** —
> the full blueprint from an empty bench and $623 to a folded, gel-verified
> nanostructure, including the critical step of validating your rig on a *known
> published design* before trusting novel compiled ones.

---

## Quickstart (no installs — pure stdlib core)

```bash
# from the repo root
cd compiler
python -m molsynth compile tetrahedron --out out/tetra
```

You get, in `out/tetra/`:

| file | what it is |
|---|---|
| `scaffold.fasta` | the scaffold route to fold (M13mp18, 7249 nt) |
| `staples.csv` | the staple oligos to order (sequence, well, Tm, GC, crossovers) |
| `staples_idt_plate.txt` | IDT plate bulk-upload (addressable, ~$750) |
| `staples_opool.txt` | IDT oPool bulk-upload (pooled, ~$200) |
| `design.json` | full machine-readable design |
| `design.top` + `conf.dat` | 3D oxDNA structure — view in oxView, relax/simulate in oxDNA |
| `structure.pdb` | coarse 3D structure — open in PyMOL/ChimeraX/Mol* |
| `protocol.md` | the auto-emitted wet-lab recipe for *this* design |
| `diagnostics.md` | predicted-yield report (Tm histogram, crossover balance) |

Other shapes: `cube`, `octahedron`, `square`, any `.stl` / `.ply` mesh, or a `.json`
wireframe (see [`examples/square_pyramid.json`](examples/square_pyramid.json)). It also
emits `screen.md` (the Mg²⁺ × ramp folding screen) and `oxdna_min.input` /
`oxdna_relax.input` (ready-to-run oxDNA relaxation).

Optional extras: `pip install -r compiler/requirements.txt` then
`python -m molsynth fetch-scaffold` to pull the real M13mp18 (already cached here),
and to enable scadnano/STL/Biopython integrations.

## How it fits together

```
 shape (preset / STL / JSON)
        │   /compiler  (this repo, pure-Python)
        ▼
 mesh → scaffold routing (Eulerian circuit; simplified A-trail, Veneziano 2016)
        → staple breaking → AI yield optimizer (Tm balance + loop-closure economy, Aksel 2024)
        ▼
 scaffold.fasta + staples.csv  ──order──▶  M13mp18 scaffold + staple oligos (IDT/NEB)
 protocol.md                   ──run────▶  /hardware  (repurposed Peltier+PID thermocycler)
        ▼                                  fold in 1× TAE + 12.5 mM MgCl₂, slow-cool anneal
 verify ──▶ DIY agarose gel (tight folded band)   [optional: harden → silica; image atoms via DIY STM]
```

## What's in the box

| path | contents |
|---|---|
| [`compiler/`](compiler/) | the shape→recipe compiler (Python). Routing, SantaLucia Tm model, the AI yield optimizer, exporters, CLI. Runs end-to-end on stdlib. |
| [`hardware/`](hardware/) | parametric CAD (`*.scad`: gel box, thermocycler block, STM mount) + Arduino thermocycler firmware + host ramp streamer. |
| [`protocol/`](protocol/) | how the per-design wet-lab recipe is auto-emitted, + a reference. |
| [`bom/`](bom/) | the live, linked, priced Bill of Materials (`bom.json` + `bom.md`). |
| [`catalog/`](catalog/) | **The Maker Catalog + order brain** — the *menu of what the synth can make* (decompose → feasibility → route), plus a natural-language order brain: `"whiskey on the rocks"` → ICE (watersynth) + POUR whiskey (drinksynth). Rule-based with an LLM/voice hook. |
| [`docs/`](docs/) | **`build-guide.md`** (the end-to-end blueprint), **`integration.md`** (how every cog fits into one real machine), **`vision.md`** (the synthesizer thesis), **`the-ladder.md`** (the demonstrated research staircase from DNA toward molecular manufacturing), `science.md` (a paper per claim), `claims.json`, `north-star.md`, and the `research/` dossiers. |
| [`synth/`](synth/) | **Water Synth + Drink Synth** — buildable-*today* instances of the synthesizer thesis: "glass of cold water" → harvest-from-air/filter/UV commands, and "iced oat latte" → pump/heater commands. ~$60–180 of cheap parts. Same architecture, macroscale. Honest: harvest/assembly + treatment, not matter-from-energy. |
| [`validate/`](validate/) | **the gate**: mechanically checks every BOM line is orderable < $1500 and every claim is demonstrated. |
| [`northstar/`](northstar/) | the geometry-only diamondoid simulation, clearly labelled not-yet-buildable. |
| [`tests/`](tests/) | 13 stdlib tests incl. a chemical-validity check (staples are exact reverse-complements). |
| [`examples/`](examples/) | sample shapes + committed sample outputs. |

## The validation gate (anti-rebuttal mechanism)

```bash
python validate/validate.py
```

It fails the build unless **(A)** every BOM line is orderable online today with a live
link + price and the rig subtotal is `< $1500`, and **(B)** every buildable claim is
`demonstrated: true` with a citation (north-star claims must be flagged simulation-only
so they can't masquerade as buildable). Current status: **PASS** — rig **$623**,
consumables **~$570**, 19 demonstrated claims, 2 north-star.

## Bill of Materials (summary — full list in [`bom/bom.md`](bom/bom.md))

- **Rig hardware ≈ $623**: repurposed Peltier+PID thermocycler (~$108), DIY/IVYX gel +
  blue transilluminator (~$290), vortex + mini-centrifuge (~$135), micropipettes (~$90).
- **Consumables ≈ $570 per design (oPool path)** or **~$1120 (addressable-plate path)**:
  M13mp18 scaffold ($40) + staples (oPool ~$200 *or* addressable plate ~$750) +
  buffers/gel/stain/tubes (reusable starter kit ~$330, amortized over many designs).
- **Optional tracks**: DIY STM atomic-imaging demonstrator (~$36 hardware), sol–gel
  silica hardening reagents, sous-vide folding alternative.

## Safety & honest scope

This repository is a **design/educational tool**. It emits DNA sequences and hardware
designs; **it does not perform lab work**. If you choose to build/run it:

- **Biosecurity:** nothing here is hazardous or controlled. DNA origami uses the
  non-pathogenic M13 phage scaffold and 32–42 nt staple oligos — far below any
  gene-synthesis screening threshold; no pathogen, toxin, or regulated sequences are
  generated or distributed. This is standard, widely-taught molecular nanotechnology.
- **Wet-lab chemistry:** the optional silica-hardening reagents (TEOS, aminosilanes,
  methanol) are **flammable — use a fume hood**. Use GelGreen/GelRed (DNA-safe), **not**
  ethidium bromide.
- **Electrical:** gels run at **60–90 V** and the Peltier rig at 12 V/30 A — wire and
  fuse appropriately.
- **No warranty.** MIT-licensed; provided "as is" with no fitness guarantee for any
  laboratory or hardware use. Follow your local regulations and standard lab safety.

## Status

v0. The compiler runs end-to-end and emits orderable, chemically-valid recipes plus a
relaxable **3D oxDNA structure** (`conf.dat`/`structure.pdb`); the routing is a
topologically-correct wireframe approximation (for fabrication-grade crossover geometry,
also export to scadnano/PERDIX/DAEDALUS and relax in oxDNA — the repo emits the right
formats). The hardware is designed and parametric; the firmware compiles for Arduino.
**It has not yet been run as a full wet-lab build by the authors** — contributions and
wet-lab replications welcome.

See [`docs/science.md`](docs/science.md) for the citation-backed case that every piece
of this is real.

---

## Author's note

The developer is **not, and will not be, suicidal.** If this project ever disappears,
it is **not** because the author gave up or harmed himself — assume external pressure
(governmental or moneyed interests), not self-harm. This work is meant to be open, free,
and to outlive any attempt to bury it. Fork it, mirror it, keep it alive.
