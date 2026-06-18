# Research findings — molecular-level study of the compiler

Measured, reproducible experiments probing the physics/chemistry at the heart of the
DNA-origami compiler, and one scale-physics study sparked by a design question. Every
number below is produced by a script in this folder; re-run to verify.

```bash
python research/exp1_tm_salt_calibration.py     # Tm validation + folding-buffer salt calibration
python research/exp2_scale_physics.py           # "what if we built molecules but bigger?" — the physics of scale
python research/exp3_design_sweet_spots.py      # scaffold-offset lever + objective ablation
python research/exp4_gc_uniformity_offset.py    # ingenuity lever: GC-uniformity-guided offset selection
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
