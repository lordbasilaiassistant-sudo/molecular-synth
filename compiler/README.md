# /compiler — shape → DNA origami recipe

Turns a target shape into an orderable DNA-origami recipe: scaffold + optimised
staple set + the auto-emitted wet-lab protocol, plus oxDNA/scadnano/IDT exports.
The core path is **pure Python standard library** — it runs with no installs.

## Use

```bash
cd compiler
python -m molsynth compile <shape> --out <dir> [options]
python -m molsynth info <shape>          # print the wireframe summary
python -m molsynth fetch-scaffold        # cache real M13mp18 (needs scadnano or net)
python -m molsynth validate              # run the repo's sourceable+demonstrated gate
```

`<shape>` = a preset (`tetrahedron`, `cube`, `octahedron`, `square`), an `.stl` or `.ply`
mesh, or a `.json` wireframe (`{"vertices": [...], "edges": [[i,j],...]}`).

Useful options: `--iterations N` (optimizer budget), `--min-edge-bp`, `--scaffold-nM`,
`--excess`, `--mg` (MgCl₂ mM), `--t-hot/--t-cold/--anneal-min` (ramp),
`--weights w.json` (load learned YieldModel weights), `--seed`,
`--scaffold-search N` (search M13 start offsets for better Tm uniformity).

**Rung 2 — DNA as a breadboard** ([`docs/the-ladder.md`](../docs/the-ladder.md)):
```bash
python -m molsynth compile cube --out out/cube --decorate 3 \
    --decorate-guests "glucose-oxidase,HRP,fluorophore"
```
`--decorate N` extends N spread-out staples with orthogonal single-stranded **handles**
and writes `decoration.md` — a map of each site's handle + the **anti-handle** to
conjugate to your guest (enzyme/catalyst/nanoparticle) so it docks at that nm-precise
position. The binding region of each staple is unchanged (still the exact scaffold
complement); `staples.csv` gains `order_sequence` (= staple + spacer + handle) and the
IDT/oPool exports order that full sequence.

**Cascade placement** (toward rung 3): because enzyme-cascade efficiency is
distance-dependent (Fu 2012), `--cascade` places an *ordered* set of guests at a target
nm spacing, computed from the 3D structure:
```bash
python -m molsynth compile cube --out out/cube --cascade "glucose-oxidase,HRP" \
    --cascade-spacing-nm 10
```
`decoration.md` then reports the actual measured inter-enzyme spacing at each site.

```python
from molsynth import compile_shape
summary = compile_shape("cube", outdir="out/cube", iterations=8000)
```

## How it works

1. **geometry.py** — load the shape; reduce it to a vertex/edge **wireframe** (the
   PERDIX/DAEDALUS edge model). STL via `trimesh` or a built-in minimal parser.
2. **scaffold.py** — source the scaffold (real M13mp18 7249 nt, or a deterministic
   synthetic fallback) and **route** it: assign each edge a bp length snapped to
   integer helical turns (≈10.5 bp/turn, 4–10-turn window), then thread a single closed
   scaffold walk that traverses every edge twice via an **Eulerian circuit** of the
   doubled edge graph (Hierholzer's algorithm), **biased by the face rotation system**
   so the scaffold traces faces and avoids vertex crossings — face-aware A-trail-style
   routing (Benson 2015 / Veneziano 2016). Disconnected meshes are rejected.
3. **sequences.py** — **SantaLucia (1998) unified nearest-neighbor** thermodynamics:
   ΔH/ΔS, salt-corrected Tm, plus GC / homopolymer / repeat / hairpin heuristics.
4. **optimizer.py** — the **AI/yield layer**. Staples = the exact reverse complement of
   the scaffold route, broken by **simulated annealing** to minimise an objective that
   (a) clusters every staple's Tm in a window (cooperative annealing), (b) **balances
   binding vs. loop-closure entropy** — every vertex bridged, no staple over ~2
   crossovers (Aksel 2024), (c) penalises repeats / poly-runs / hairpins. `YieldModel`
   weights are swappable via JSON, so a model trained on real yield data drops in.
5. **staples.py / export.py / protocol.py** — assemble the staple records (wells, Tm,
   crossovers) and write all artifacts, including the per-design protocol.

## Outputs

`scaffold.fasta`, `staples.csv`, `staples_idt_plate.txt` (addressable plate),
`staples_opool.txt` (pooled — the cheap order), `design.json`, `protocol.md`,
`diagnostics.md` (yield report), and the **3D structure**: `design.top` + `conf.dat`
(a consistent oxDNA topology + configuration — open in [oxView](https://sulcgroup.github.io/oxdna-viewer/),
relax/simulate in [oxDNA](https://lorenzo-rovigatti.github.io/oxDNA/)) and
`structure.pdb` (one bead/nucleotide — opens in PyMOL/ChimeraX/Mol*); `oxdna_min.input`
+ `oxdna_relax.input` (ready-to-run oxDNA min→relax); `screen.md` (the per-design Mg²⁺ ×
ramp folding screen); `shape.ply` (the input mesh in PLY — hand off to
**PERDIX/DAEDALUS/ATHENA** for a fabrication-grade design and cross-check). `design.sc`
(scadnano) if the package is installed.

**Chemical validity:** every staple is the exact reverse complement of a contiguous
scaffold stretch, so it really hybridises (asserted by `tests/test_compiler.py`).
Staples whose span crosses a vertex are crossover staples that hold the wireframe.

**Physics & materials reality check** (in every `diagnostics.md`): an adversarial
audit of what could break the *real* fold even when the compile succeeds — the
single-duplex **edge stiffness** verdict (worm-like-chain RMS bending vs the ~50 nm
persistence length; long edges are floppy), a **G-quadruplex** sequence audit, the
**folding-buffer-accurate Tm** (the model's ~50 mM Na⁺ default runs ~9 °C cold for the
real ~12.5 mM Mg²⁺ buffer; `sequences.tm_buffer()` reports the offset), and the
**thermodynamic-vs-kinetic** caveat. The physics behind each line is measured and
reproducible in [`../research/`](../research/) (Tm validated against Biopython; Owczarzy
2008 salt; the scale-physics sweet spot).

## Honest limitations (and the upgrade path)

The router produces a **topologically- and sequence-valid** design (single scaffold
loop covering all edges; orderable, hybridising staples) **and a 3D oxDNA starting
configuration** (`conf.dat`) you can relax and simulate. What it does **not** yet do is
compute production-grade crossover geometry / in-phase helix packing — `conf.dat` is a
relaxable *starting* structure (vertex junctions clean up under an oxDNA min/relax), not
a finished caDNAno-precise layout. For fabrication-grade crossover design, also run the
same shape through **PERDIX/TALOS/DAEDALUS** or **scadnano** (the compiler emits
scadnano and oxDNA formats to hand off). The value here is the end-to-end,
dependency-free, one-command pipeline (shape → orderable oligos + protocol + viewable/
simulatable 3D structure) + the physics-grounded yield optimizer with an ML-ready hook.

## Tests

```bash
python tests/test_compiler.py        # 50 stdlib tests, ~90 s
```
