# science.md — why Molecular Synth v0 is real

**Every capability this rig claims is backed by a peer-reviewed lab demonstration.**
The machine-readable list lives in [`claims.json`](claims.json) and is enforced by
[`/validate`](../validate/validate.py): a claim only counts if it is on the
`buildable` track **and** marked `demonstrated: true` with a citation. Anything not
yet demonstrated (diamondoid mechanosynthesis, macroscopic assembly) is quarantined
on the `north-star` track and described in [`north-star.md`](north-star.md) — clearly
labelled simulation-only so it can never masquerade as buildable.

> **Honest scope, stated once and plainly:** the output of this rig is a
> **DNA-self-assembled nanostructure, ~10 nm – ~1 µm** (single particles; micron-scale
> with hierarchical assembly), optionally **hardened into silica or metal**. It is
> **not** a macroscopic object, and it is **not** Drexler diamondoid mechanosynthesis.
> What it *is* is the only experimentally-demonstrated route to programmable,
> sequence-addressed, atomically-defined matter you can run on a desk for ~$1k.

The detailed dossiers (with full reasoning, alternative sources and the adversarial
validation) are in [`research/`](research/). This file is the distilled spine.

---

## 1. The thing actually works: scaffolded DNA origami

A single ~7 kb single-stranded **scaffold** (the M13mp18 phage genome, 7249 nt) is
folded into a designed shape by ~200 short synthetic **staple** oligos that bind the
scaffold at multiple points and pin it via crossovers. The whole process is *one pot*:
mix scaffold + staples in a Mg²⁺ buffer, heat, cool. ~10¹²–10¹⁴ copies fold in
parallel from a picomole-scale reaction.

- **2D arbitrary shapes** — Rothemund, *Nature* 440:297 (2006). `[origami-2d]`
- **3D solids (honeycomb lattice) + caDNAno CAD** — Douglas et al., *Nature* 459:414
  (2009). `[origami-3d-cadnano]`
- **3D "voxel" bricks** — Ke et al., *Science* 338:1177 (2012). `[dna-bricks]`
- **Micron-scale / gigadalton via hierarchical assembly** — Wagenbauer et al.,
  *Nature* 551:78 (2017); Tikhomirov et al., *Nature* 552:67 (2017).
  `[hierarchical-micron]`

This is the most reproduced result in molecular nanotechnology. It is not in dispute.

## 2. You can compile a shape → recipe automatically (the software)

The hard part is design, and it is **solved and automated**:

- **Top-down inverse design** — input a geometric mesh, output the full scaffold route
  + every staple sequence, no manual editing: Veneziano et al. (DAEDALUS), *Science*
  352:1534 (2016); open-source `pyDAEDALUS`. `[top-down-routing]`
- **Mesh → wireframe DNA** — Benson et al. (vHelix), *Nature* 523:441 (2015).
  `[mesh-to-dna]`
- **Automated wireframe suites** (PERDIX/TALOS/METIS/ATHENA) — Jun et al., *Sci. Adv.*
  5:eaav0655 (2019) and companions. `[automated-wireframe-suite]`
- **In-silico validation before you spend money on oligos** — oxDNA coarse-grained
  model, Ouldridge et al. *J. Chem. Phys.* 134:085101 (2011); oxDNA2, Snodin et al.
  (2015). `[oxdna-sim]`

`/compiler` implements the core of this pipeline from scratch (mesh → face-aware
A-trail-style scaffold routing — a single Eulerian circuit biased by the face rotation
system to trace faces and avoid vertex crossings → staple breaking → orderable sequences
+ protocol), and exports to the standard ecosystem formats (oxDNA topology, scadnano,
IDT plate / oPool). It is dependency-light by design so it runs end-to-end offline.

## 3. The "AI / yield" layer is honest physics, and it's the moat

Folding yield is governed by known determinants, each peer-reviewed:

- **Tm balancing for cooperative annealing** — staples whose folding temperature
  clusters together bind near-simultaneously and out-compete kinetic traps. Tm from
  the unified nearest-neighbor model: SantaLucia, *PNAS* 95:1460 (1998). `[nn-thermo]`
- **Loop-closure / hybridization balance** — *the* under-used lever: yield depends on
  the **balance** between a staple's binding and its scaffold loop-closures (each
  closure pays an entropic penalty), so naively maximizing binding length can hurt. A
  thermodynamics-aware staple-break optimizer that balances the two gave large,
  design-specific accuracy/yield gains (e.g. ~2%→61% on a test block; gel + TEM): Aksel
  et al. (Douglas lab), *PNAS* 121:e2406769121 (2024); open `pyOrigamiBreak`. Not a
  universal "6–30×", and not a neural net — physics + classical optimization.
  `[loop-closure-yield]`
- Plus repeat-, hairpin- and poly-run penalties grounded in known failure modes.

`/compiler`'s optimizer implements this objective (simulated annealing over break
points, scoring = Tm window + loop-closure penalty + coverage + sequence quality) with
an **ML-ready scoring hook** (`YieldModel.load()` swaps in learned weights). We claim
*physics + classical optimization that reproduces published yield gains, packaged
one-click* — **not** a black-box neural net. That honesty is deliberate: it is what
removes the easy rebuttal.

## 4. Folding needs only a programmable temperature box

- The folding reaction is a single anneal in **1× TAE + 12.5 mM MgCl₂**, staples at
  5–10× excess; Rothemund (2006); Castro et al. *Nat. Methods* 8:221 (2011).
- A qPCR thermocycler is **not** required: many designs fold **isothermally** at one
  constant temperature, some in minutes — Sobczak et al., *Science* 338:1458 (2012).
  `[isothermal-fold]` So a Peltier+PID block (or even a sous-vide bath) suffices. The
  compiler emits the exact ramp; `hardware/firmware/thermocycler.ino` runs it.

## 5. You can verify it folded — cheaply

- **Agarose gel electrophoresis** is the workhorse QC: a folded origami runs as one
  tight band, distinct from excess staples (fast front) and aggregates (smear/well).
  Castro et al. (2011), Suppl. Protocol 3. Run cold, with Mg²⁺ in the buffer, 60–90 V.
  `[gel-qc]`
- **PEG-8000 precipitation** purifies it with just a microcentrifuge — Stahl et al.,
  *Angew. Chem.* 53:12735 (2014). `[peg-purification]`
- **Atomic resolution is real and cheap** — a ~$300 hobby STM resolves the HOPG atomic
  lattice: Ma, *HardwareX* 17:e00504 (2023); Berard open STM. Honest caveat: the STM
  images **graphite atoms, not the soft origami** — it is the atomic-resolution
  *capability demonstrator*, decoupled from product QC. `[hobby-stm-atoms]`

## 6. Hardening: soft DNA → rigid inorganic replica

The DNA template is converted into a hard material:

- **Sol–gel silicification (primary, DIY)** — DNA → SiO₂ composite, ~3 nm fidelity,
  ~10× stiffer, done in a tube at room temperature with TEOS + an aminosilane:
  Liu et al., *Nature* 559:593 (2018); Nguyen/Heuer-Jungemann et al., *Angew. Chem.*
  58:912 (2019); protocol in Jing et al., *Nat. Protoc.* 14:2416 (2019).
  `[silicification]` `[silica-shell]`
- **Metal casting (stretch)** — DNA mold + gold seed → solid Au/Ag nanostructures:
  Sun et al., *Science* 346:1258361 (2014); Helmi et al., *Nano Lett.* 14:6693 (2014).
  `[metal-casting]`
- **ALD oxide (service-only)** — conformal Al₂O₃/TiO₂/ZnO/IrO₂; demonstrated but needs
  a vacuum reactor (~$30k+), so route to an external nanofab, **not** the desktop BOM:
  Shen/Keller et al., *Beilstein J. Nanotechnol.* 8:2503 (2017); ALD-on-origami-crystals,
  *JACS* 147 (2025). `[ald-oxide]`

## 7. The economics are real too

Staple synthesis dominates marginal cost; pooled synthesis (IDT oPools) is markedly
cheaper than addressable plates, and reusing excess staples cuts it further — Isinelli
et al., *Nucleic Acids Research* 53(11):gkaf527 (2025). The compiler emits **both** a
$200 oPool order and a $750 addressable-plate order so the user picks the cost point.
`[staple-cost]`

---

## What is NOT claimed (the rebuttal firewall)

| Tempting overclaim | Reality | Where |
|---|---|---|
| "Builds macroscopic objects" | No — nano-to-micron only | scope line above |
| "Diamondoid / atom-by-atom hard matter" | Theory/DFT only, never demonstrated | [`north-star.md`](north-star.md) `[ns-diamondoid-mechanosynthesis]` |
| "AI designs sequences from scratch" | It's physics + classical optimization | §3 |
| "Learned yield predictor, validated" | Experimental add-on only | §3 |
| "STM images our origami" | STM images HOPG atoms, not origami | §5 |
| "ALD coating at home" | Vacuum reactor; external service | §6 |

The `buildable` track claims only demonstrated science. The ambition lives, fully and
honestly, on the `north-star` track — simulated, labelled, and never costed into the
BOM.
