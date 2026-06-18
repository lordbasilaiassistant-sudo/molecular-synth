# Research findings — molecular-level study of the compiler

Measured, reproducible experiments probing the physics/chemistry at the heart of the
DNA-origami compiler, and one scale-physics study sparked by a design question. Every
number below is produced by a script in this folder; re-run to verify.

```bash
python research/exp1_tm_salt_calibration.py     # Tm validation + folding-buffer salt calibration
python research/exp2_scale_physics.py           # "what if we built molecules but bigger?" — the physics of scale
python research/exp3_design_sweet_spots.py      # scaffold-offset lever + objective ablation
python research/exp4_gc_uniformity_offset.py    # ingenuity lever: GC-uniformity-guided offset selection
python research/exp5_why_scale_matters.py       # WHY size matters at bedrock, and the dodge
python research/exp6_physics_redteam.py          # adversarial physics/materials audit of the end product
python research/exp9_kinetic_ladder.py            # kinetic folding-ORDER term (optional, default OFF): Tm-ladder
python research/exp10_hierarchy.py               # hierarchy: origami unit cells -> super-lattice (compose the scales)
```

Deps: Biopython (independent NN thermodynamics) for exp1; pure stdlib for exp2/exp3.

---

## Exp 1 — the Tm model is correct, but mis-calibrated for its own buffer

**Validation.** molsynth's nearest-neighbor Tm (`compiler/molsynth/sequences.py`, SantaLucia
1998) matches Biopython's independent `DNA_NN3` table to **mean |ΔT| = 0.86 °C** (max 3.3 °C)
over 400 random 32–42 nt staples, with matched 62.5 nM strand concentration and the same
Owczarzy-2004 monovalent salt correction. **The implementation is sound.**

**Calibration gap (the finding).** The compiler defaults to `na_M = 0.05` (50 mM Na⁺), but
origami folds in **12.5 mM MgCl₂**. Mg²⁺ stabilises duplexes far more than its naive monovalent
equivalent. Against the physically-correct Owczarzy-2008 divalent model (Biopython `saltcorr=7`,
`Mg=12.5`):

| [Na⁺] used in molsynth | mean Tm gap vs Mg²⁺ ground truth |
|---|---|
| 13 mM (docstring's `120·√[Mg]` rule) | **−21.9 °C** (badly wrong) |
| 50 mM (current default) | **−8.9 °C** (too low) |
| ~166 mM (buffer-accurate equivalent) | ≈ 0 °C |

So the default under-predicts folding-buffer Tm by **~9 °C**, and the docstring's rule-of-thumb
is ~22 °C low. **Recommendation:** set the diagnostics/protocol Tm to `na_M ≈ 0.166` (or add a
proper `mg_mM` path using the Owczarzy-2008 correction). A uniform offset does **not** change the
optimiser's *relative* cut-placement search (variance term is offset-invariant), but it does fix
the absolute Tm window penalty and the numbers a wet-lab user reads. This couples to Exp 3(B).

Refs: SantaLucia 1998 (PNAS 95:1460); Owczarzy 2004 (Biochem 43:3537); Owczarzy 2008 (Biochem 47:5336).

---

## Exp 2 — "what if we built molecules, but bigger?" (the physics of scale)

A creative prompt: the universe feels recursively self-similar, so could we reconstruct a
molecule at a graspable size and make, e.g., giant food? The honest physics has **two true
halves**:

1. **Structure** *can* be self-similar across scale — fractals, critical phenomena, turbulent
   cascades, the renormalization group. The "patterns repeat up/down" intuition is real.
2. **Forces are not scale-invariant.** The dimensionless ratios (surface/volume,
   gravity/thermal, binding/thermal) change with linear size *L*, so a **different force
   dominates at each scale**. You cannot "scale a molecule up": a bond is ~0.15 nm of quantum
   orbital overlap — stretch it and it stops being a bond. Properties (taste, color, stiffness,
   melting) are *emergent at their scale*.

Computed crossovers (300 K, ρ≈1100 kg/m³, σ_bind≈20 mJ/m²):

- **Gravity = thermal at L ≈ 0.79 µm.** Below: the Brownian/colloidal world — objects shuffle
  themselves and *self-assemble*. Above: gravity wins — it just falls and sits, you need hands.
- **Self-transport by thermal motion:** a 50 nm origami diffuses **4.2 µm/s** (≈80× its body
  length) — it finds its own binding partners. An apple "diffuses" **4 nm/s** — frozen.
- **Binding beats thermal noise** for any interface ≳ 0.5 nm; by ~10 nm assemblies are robustly
  multi-*kT* and hold a programmed shape.

**The manipulation/self-assembly sweet spot is ~10 nm – 0.8 µm** — small enough that thermal
motion builds it for free by the trillions, large enough to hold a designed shape and be
addressed/imaged. **That is exactly the DNA-origami window this repo compiles.** The honest path
molecule→macroscopic is **hierarchical self-assembly** (glucose → cellulose → cell wall →
lettuce — which nature already runs for food), not inflating one molecule. Our buildable lever is
to *program the bottom rung* (origami) and let hierarchy carry it up. See `docs/north-star.md`
for why macroscopic atom-up replication stays north-star.

---

## Exp 3 — where the compiler's design levers actually pay off

**(A) Scaffold-offset is a big free lever.** M13mp18 is circular, so the route's start position
is free. Over 24 offsets (octahedron), the yield proxy ranges **best 73 → worst 205** (spread
132; the worst start is ~3× worse). The compiler's 8-sample search lands within **6.4** of the
global optimum — so the search is genuinely worth it, and there is modest headroom for a smarter
search (more samples, or GC-uniformity-guided — see below).

**(B) Which molecular terms do real work** (octahedron; Δ = how much worse the design gets under
the full objective when a term is removed):

| term removed | Δ full-score | reading |
|---|---|---|
| Tm-window | **+8.85** | dominant — absolute Tm targeting matters most |
| internal-repeat | +5.21 | M13 k-mer repeats are real |
| hairpin | +4.87 | self-structure matters |
| Tm-variance | +1.91 | modest (and delicate — see prior session) |
| loop-entropy | −1.3 | ~slack for a small shape (matters on large presets) |
| off-target | −1.0 | ~slack here (few long repeats span a short edge) |

**Key molecular insight:** the staple **Tm spread stays ~6.4 °C across every ablation** — it is
floored by M13's *intrinsic local GC heterogeneity*, not by where you cut. Cooperative annealing
(the high-yield lever, Aksel 2024) is therefore limited by the scaffold sequence itself.

**Coupling to Exp 1 (a concrete, testable improvement).** Octahedron staples already average
**66 °C** at the (under-calibrated) 50 mM — *above* the optimiser's `tm_hi = 64`. The
buffer-correct +9 °C pushes the real mean to ~75 °C, far above the window, so the optimiser is
fighting a mis-calibrated target. The coherent fix is to **recalibrate `na_M` and shift the Tm
window together** (≈ [59, 73] °C) so the dominant objective term targets real folding-buffer
temperatures.

---

## Exp 4 — the ingenuity sweet spot, confirmed: pick the offset for GC-uniformity

Exp 3 said the Tm-spread floor is set by M13's GC landscape and the offset is free. **Tested and
confirmed:** across 16 octahedron offsets, the windowed-GC standard deviation of the routed
region correlates with the staple Tm spread the optimiser actually achieves at

**Pearson r = +0.73.**

Achieved Tm-sd ranges **2.94 → 6.47 °C** across offsets — so selecting the most GC-uniform start
could roughly **halve** the cooperative-annealing Tm spread versus the worst, a direct
high-yield lever (Aksel 2024). The compiler currently ranks offsets by the general yield proxy,
which captures this only indirectly. **Concrete improvement:** add a GC-uniformity term to the
offset ranking in `compile_shape()`'s scaffold search — cheap (no extra anneal) and targets the
one floor that cut-placement cannot move. This is the highest-leverage, lowest-risk next step,
and it stacks with the Exp 1 buffer recalibration.

---

## Exp 5 — WHY size matters at bedrock, and the dodge

The root cause is **geometry of exponents, not a wall**. Every force is sourced by a
different-dimensional feature of an object, so each scales as a different power of linear size L
(measured slopes, log-log):

| quantity | exponent n (E ∝ Lⁿ) | sourced by |
|---|---|---|
| thermal kT | **0** (constant!) | one degree of freedom — scale-free |
| surface (vdW, adhesion, drag, tension) | **2** | interfaces (area) |
| gravity / weight | **3–4** | amount of stuff (volume) |
| diffusive reach per second | **−0.5** | thermal vs viscous drag |

A "crossover scale" is simply where two lines of different slope intersect (gravity = thermal at
~0.79 µm). **The bedrock that cannot be dodged:** the atomic scale is pinned by the fundamental
constants — the Bohr radius `a₀ = 4πε₀ℏ²/(mₑe²) = 0.053 nm` derives from raw constants in the
script. Bonds (~0.15 nm), bond energy (~eV), and kT (~0.026 eV) are all set there. There is no
"bigger atom," and kT is scale-free — so as you move away from the atomic scale, the *count* of
fundamental units (atoms, bonds, area, volume) changes and each force, caring about a different
count, re-sorts. That is the entire origin of why size matters.

**Why you can't "have it all ways" in one object — and the dodge.** A *monolithic* object has
one size, so the L³-vs-L²-vs-L⁰ competition already picked a winner; it can't be both
thermally-self-assembling (needs small) and rigidly gravity-defying (needs big). But a
**multi-scale** object can. Nature never accepts the 1/L surface penalty: it makes area fractal,
A ∝ L^D with D→3. A solid 15 cm sphere has 0.07 m² of surface; a 15 cm human lung packs **~75 m²
(>1000× more)** by nesting airways across scales — molecular-scale surface chemistry *and*
macroscopic size simultaneously. Bone, wood, nacre, gut, mitochondria all do this. **You don't
break the scaling laws; you compose them across scales** (paying structural complexity + energy).
That — not inflating a molecule — is "the missing something," and it's exactly the lever DNA
origami opens at the bottom rung (program the smallest scale; let hierarchy carry it up). Two
further escapes the passive laws don't see: **active matter** (burn energy to fight the scaling,
as living cells do) and **metamaterials** (engineered structure gives bulk properties the base
chemistry "shouldn't" have).

---

## Exp 6 — physics & materials red-team (audit the end product like code)

Thinking like a security auditor, but the "exploits" are physical assumptions that break the
*real folded object* even when `compile_shape()` succeeds and every file is written. Findings
(audited over the 11 committed designs):

| # | severity | finding | evidence | the lever (not a wall) |
|---|---|---|---|---|
| F1 | HIGH | single-duplex wireframe edges are thermally **floppy** | every edge ~63 bp → RMS bend **~38°** (WLC, Lp≈50 nm); 11/11 designs | stiffness is a *design variable*: multi-helix-bundle edges (6HB Lp ~1–10 µm, ~20–70× stiffer) → large rigid shapes. **Now reported in diagnostics.** |
| F2 | HIGH | Tm mis-calibrated for the Mg²⁺ buffer | Exp 1: real staples ~**+9 °C** hotter than the 50 mM default | `sequences.tm_buffer()` added; diagnostics report the offset. Next: shift the optimiser window +9 °C. |
| F3 | MED | G-quadruplex sequestration not screened | audited **490 staples → 0 G4 motifs** (clean today) | `g_quadruplex_sites()` added + reported; promote to an optimiser term before novel/denser sequences. |
| F4 | MED | objective is thermodynamic; folding is **kinetic** | no topological-order term (optimizer.py); pathway control matters (Dunn 2015; Sobczak 2012) | program a Tm ladder matched to assembly order (seams last) → kinetic programming toward ~100% yield. |

**What shipped from this audit (additive, no orderable output changed):** a *Physics & materials
reality check* section in every `diagnostics.md` (edge-stiffness verdict, G4 audit,
buffer-accurate Tm offset, kinetic caveat), backed by three new validated functions in
`sequences.py` (`tm_buffer`, `g_quadruplex_sites`, `wlc_rms_bend_deg`) and 4 new tests. The
digital pipeline was already sound; these are the physics gaps that decide whether the *atoms*
cooperate — and none of them is a wall. Each is a design lever toward making the impossible
buildable.

---

## Exp 10 — hierarchy: compose the scales (the next rung toward macroscopic)

Exp 2/5 said the honest molecule→macro path is *hierarchical self-assembly*, not inflating one
molecule. Exp 10 makes that ladder quantitative for **this repo's output**: take a cube origami
unit cell (~40 nm), let it tile a 3D lattice via sticky-end handles (4 units/edge per level), and
recurse. At each level we compute the two physics crossovers that decide whether the rung
self-builds — **gravity vs thermal** (exp2's `(kT/ρg)^¼` form, identical constants) and **handle
binding vs thermal**.

**The measured self-assembly ladder** (300 K, ρ=1100 kg/m³, 4 handles/interface, 8-bp sticky ends):

| level | units | size | gravity/kT | diffuse/s | bind/kT | regime |
|---|---|---|---|---|---|---|
| 0 | 1 | 40 nm | 6.7e-6 | 4.7 µm/s | 47 | self-assembles |
| 1 | 64 | 160 nm | 1.7e-3 | 2.3 µm/s | 47 | self-assembles |
| 2 | 4,096 | 640 nm | 0.44 | 1.2 µm/s | 47 | self-assembles |
| 3 | 262,144 | 2.6 µm | 1.1e+2 | 586 nm/s | 47 | **too heavy → falls/sits** |
| 4 | 1.7e7 | 10 µm | 2.9e+4 | 293 nm/s | 47 | too heavy |
| 5 | 1.1e9 | 41 µm | 7.3e+6 | 146 nm/s | 47 | too heavy |
| 6 | 6.9e10 | 164 µm | 1.9e+9 | 73 nm/s | 47 | too heavy |

**Finding 1 — self-assembly has a hard ceiling, and it is exactly exp2's.** The gravity = thermal
crossover lands at **L ≈ 0.79 µm** (787 nm) — the same number exp2/exp5 derive, because it is the
same `(kT/ρg)^¼` with the same constants. So free Brownian super-assembly carries you up to about
**level 2 (640 nm, ~4,000 units)**; at **level 3 (2.6 µm)** gravity already beats thermal by ~100×
and the trillion-fold Brownian search that built the bottom rung dies. That is not a wall — it is
the **measured hand-off point** where you must switch mechanism (silica/metal hardening = rung 1 of
the-ladder.md, templated placement, or active/energy-burning assembly).

**Finding 2 — super-assembly stability is monotonic in handle valence (the bottom-rung design
lever).** Per-handle binding free energy is **~1.7 kT for a 4-bp toehold, ~11.7 kT for an 8-bp
sticky end** (NN free energy ~1.5 kcal/mol·bp, net of the ~+5 kcal/mol nucleation/entropy penalty).
Total interface binding is strictly increasing in handle count for both lengths (verified 1→12
handles): a weak 4-bp handle needs ~2 handles to clear the ~3-kT "stays together" bar and ~5 to be
robust, while an 8-bp handle is robustly multi-kT almost alone. **Valence + handle length is the
programmable knob** that decides whether the lattice holds, and it sits squarely in the window this
compiler already targets.

**The honest read:** origami (~40 nm) is right in the exp2 sweet spot; a couple of levels of
handle-driven tiling reach ~0.6 µm blocks that *still* self-assemble — then gravity takes over. You
don't inflate the molecule, you **compose scales and switch mechanism at the measured 0.79 µm
crossover**. Self-contained, no compiler-core change; self-checks assert the crossover matches
exp2's ~0.79 µm and that binding-vs-kT is monotonic in handle count.

## Exp 9 — a kinetic Tm-ladder term (addresses F4): program folding ORDER, not just the endpoint

Exp 6/F4 flagged that the objective is **thermodynamic** (equilibrium Tm clustering) and ignores
folding **ORDER** — yet folding is kinetic: as the pot cools, staples bind in descending-Tm
order, so the hottest engage first. If a loop-/seam-closing staple is also among the hottest it
can close before its framework nucleates → a kinetic trap (Sobczak et al., Science 338:1458, 2012;
Dunn et al., Nature 525:82, 2015).

**What shipped (OPTIONAL, default OFF — existing behaviour byte-identical):** a `w_kinetic` term
(`optimizer.kinetic_penalty`, default weight **0.0**). A staple's *load* = (# crossovers it
bridges) + `kinetic_loop_w`·ln(largest enclosed loop); the term penalises the positive covariance
between load and Tm, rewarding a gradient where high-load (seam) staples are NOT the hottest. A
default model (`w_kinetic=0`) scores **exactly** (`==`) a pre-term model, so no committed output
changes.

**Measured (cube, seed 12345, 3000 iters; `research/exp9_kinetic_ladder.py`):**

| metric | term OFF (default) | term ON (w_kinetic=8) |
|---|---|---|
| Pearson r(crossover-count, Tm) | +0.043 | **+0.012** |
| Pearson r(crossover+loop load, Tm) | +0.071 | **+0.029** |
| kinetic covariance (penalty) | 0.186 | **0.075** (−60%) |
| mean Tm: crossover − non-crossover staples | +0.53 °C | **+0.15 °C** |

So enabling the term measurably drives crossover-heavy staples toward the COOL end (framework
nucleates first). A deterministic unit check confirms the penalty correctly ranks a *framework-first*
ladder (cost 0) below a *seam-first* one (cost 1.67).

**Honest structural finding (why the lever is modest on the presets):** the existing length window
(staples ≤ 42 nt) is *shorter* than the ~63 bp inter-crossover spacing of these single-duplex
wireframes, so **a staple physically cannot bridge two crossovers — max crossover-load is 1 for
every preset.** The term's lever here is the binary crossover-vs-framework Tm ordering and the
enclosed-loop size; it bites hardest on **denser / multi-helix-bundle designs** (the F1 stiffness
fix) where staples do carry >1 crossover. This is a **kinetic PROXY** built from the equilibrium
Tm ranking — there is **no MD kinetic simulator** — and it stays a design lever toward the
~100%-yield kinetic programming that F4 points at.
