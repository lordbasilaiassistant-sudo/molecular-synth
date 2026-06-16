# 06 — The "Staple-Routing for Max Yield" Layer: What Is Honestly Claimable as a Software Moat

> **Correction note (canonical framing is in [`../claims.json`](../claims.json) `[loop-closure-yield]`):**
> The "6–30×" figure below is Aksel 2024's own abstract number, but it is
> **design-specific, not a universal multiplier** (e.g. ~2%→61% on a test block). The
> mechanism is a **balance** between staple hybridization and loop-closure entropy —
> **not** crossover-*minimization dominance*. Read the gains in the dossier with that
> qualifier; the gated `claims.json` already carries it.

**Domain:** The AI/ML / algorithmic layer of the Molecular Synth v0 compiler that takes a scaffold routing and emits a *staple recipe* (the set of short oligo sequences you actually order) chosen to **maximize DNA-origami folding yield**.

**Bottom line up front (honesty first):**
The yield-optimization layer is **real and valuable, but it is almost entirely heuristic / physics-model optimization, NOT deep learning.** The single best-validated result in the field (Aksel et al., *PNAS* 2024) is a **shortest-path graph optimization driven by a closed-form nearest-neighbor thermodynamic model + simple loop-entropy terms** — it gave **6–30× experimentally measured yield improvements** with *no neural network at all*. "ML" in DNA nanotech today is overwhelmingly used for *image-based yield measurement* (CNNs counting good structures in TEM images), not for *sequence design*. So the honest moat claim is:

> "A physics-grounded staple-break optimizer (nearest-neighbor thermodynamics + loop-closure entropy + sequence-quality penalties, optimized by simulated annealing / shortest-path) that reproduces the published 6–30× yield gains, packaged into a one-click shape→recipe compiler."

That is buildable, defensible, and does **not** require us to overclaim a learned model. A learned scoring model is an *optional upgrade*, not the foundation.

---

## 1. What actually determines DNA-origami folding yield

DNA origami (Rothemund 2006) folds a long single-stranded scaffold (~7,250 nt M13mp18 is canonical) with ~200 short "staple" strands that crossover between helices to pin the scaffold into a shape. Yield = fraction of scaffold copies that fold into the correct, monomeric, defect-free target. The determinants below are each supported by peer-reviewed work.

### 1.1 Staple length (~18–50 nt; sweet spot ~32–42 nt)
Each staple is typically broken so that its binding domains sum to roughly 32–42 nt, split across 2–3 crossovers (~7–8 turns of helix per staple in the classic honeycomb/square lattice). Too short → too weak to nucleate and stay bound at the folding temperature; too long → kinetic traps and reduced specificity. caDNAno (Douglas et al. 2009) enforces the lattice geometry that produces this length regime, and Aksel 2024 uses a default length window of 21–60 nt with the optimizer choosing within it.

### 1.2 Crossover count per staple (the dominant, under-appreciated term)
Aksel et al. 2024's central experimental finding: **limiting the number of crossovers (scaffold loop closures) per staple should be prioritized over simply extending the staple's binding length.** Each crossover forces the staple to clamp two *non-contiguous* scaffold segments together, paying an **entropic loop-closure penalty**. When that penalty dominates, adding more binding base pairs actually *hurts* folding. This is the term most CAD tools ignore and is the strongest single lever for yield.

### 1.3 Melting-temperature (Tm) balancing across staples — cooperative annealing
During a thermal anneal the structure folds over a narrow temperature window; staples whose effective Tm (folding temperature, T_fold) clusters together bind **cooperatively and nearly simultaneously**, which favors the correct global structure over kinetic traps. Staples that are thermodynamic outliers (much weaker or much stronger than the ensemble) misfold or fail to incorporate. The design goal is therefore not "max Tm" but "**every staple's predicted T_fold inside a tight target window**" so the whole set crosses its folding transition together. T_fold is computed per staple from a nearest-neighbor model (Section 3). Sobczak/Dietz 2012 showed structures fold isothermally within seconds at a temperature right at T_fold, underscoring that getting all staples to share one T_fold is what enables high-yield, fast folding.

### 1.4 Sequence symmetry / repeat minimization (unique addressability)
If two different scaffold regions share a long repeated subsequence, a staple meant for one site can bind the other → mis-paired, off-target structures. The standard M13mp18 scaffold has >100 repeats ≥8 nt long (including 29-, 30-, and 42-nt repeats), an intrinsic ceiling on addressability (Nguyen et al. / Jabbari work on uniquely addressable scaffolds). Origami compilers therefore penalize staples (or scaffold routings) that create repeated k-mers. Synthetic de Bruijn–style scaffolds are designed specifically to suppress all repeats below a chosen length.

### 1.5 Secondary structure / hairpin avoidance
A staple (or scaffold region) that folds back on itself competes with the intended staple–scaffold duplex. Rothemund deliberately routed *around* M13 bases ~5515–5587 because that region contains a strong, biologically functional hairpin. Practically: avoid self-complementary stretches in the staple and avoid forcing a staple to bind a structured scaffold region.

### 1.6 GC content & poly-runs
GC pairs contribute ~3 H-bonds and stack more strongly than AT (2 H-bonds), so local GC content drives the per-staple Tm; balancing GC keeps T_fold uniform (ties back to 1.3). Long poly-runs (e.g. ≥4–5 G's → G-quadruplex risk; long A/T runs → weak, low-Tm domains and synthesis/coupling errors) are penalized.

---

## 2. Honest map: heuristic optimization vs. genuine ML

| Capability | What it actually is | Demonstrated? |
|---|---|---|
| **Staple-break optimization for yield (Aksel 2024, pyOrigamiBreak)** | Closed-form NN thermodynamics + loop-closure entropy → **k-shortest-path** over a break-point graph. Pure physics + classical graph optimization. | **YES — 6–30× yield gains, agarose gel + TEM** |
| Scaffold routing via **shape annealing** (Babatunde 2021) | **Simulated annealing** + shape grammar generating routings. Classical metaheuristic, computational only. | Computational only |
| Generative design of wireframe origami (Vfold/NAR 2025) | Generative/heuristic search over routings. | Mostly computational |
| **"ML for DNA origami"** in practice | **CNNs/YOLO counting good vs. bad structures in TEM/AFM images** to *measure* yield. Genuine deep learning — but for *characterization*, not sequence design. | YES (image analysis) |
| Learned sequence→yield scoring model | Aspirational. No published, validated model predicts origami yield from staple sequence end-to-end well enough to replace the physics model. | NO (north-star) |

**Takeaway for our moat:** build the *physics + classical-optimization* engine (proven). Offer a *learned scoring function* only as a drop-in replacement for the hand-tuned objective, trainable later on our own gel/TEM yield data — labeled clearly as experimental.

---

## 3. The nearest-neighbor (NN) thermodynamic model — codeable spec

This is the exact, implementable core. Tm of each staple binding domain is computed with the **unified SantaLucia nearest-neighbor parameters** (SantaLucia 1998; the underlying oligo set is Allawi & SantaLucia 1997, distributed in Biopython as `DNA_NN3`). These are the canonical, machine-readable values primer3/Biopython use.

### 3.1 Free energy / enthalpy / entropy of a duplex
For a duplex read 5'→3' on the top strand, sum over each overlapping dinucleotide (NN) step, then add initiation and (if self-complementary) symmetry terms:

```
ΔH_total = Σ ΔH(NN_i) + ΔH_init(5'-end) + ΔH_init(3'-end) [+ ΔH_sym]
ΔS_total = Σ ΔS(NN_i) + ΔS_init(5'-end) + ΔS_init(3'-end) [+ ΔS_sym]
```

ΔH in **kcal/mol**, ΔS in **cal/(mol·K)** (i.e. e.u.). The init term applied at each end depends on whether that terminal base pair is A·T or G·C.

### 3.2 The parameter table (SantaLucia-unified / Biopython `DNA_NN3`)
Keys are written as `TOP/BOTTOM` where BOTTOM is the complement read 3'→5'. Values are `(ΔH, ΔS)`.

```python
# ΔH in kcal/mol, ΔS in cal/(mol·K).  Source: Allawi & SantaLucia 1997 /
# SantaLucia 1998 unified set (Biopython Bio.SeqUtils.MeltingTemp.DNA_NN3)
NN = {
    "init":        (0.0,   0.0),
    "init_A/T":    (2.3,   4.1),    # apply once per A·T terminal base pair
    "init_G/C":    (0.1,  -2.8),    # apply once per G·C terminal base pair
    "sym":         (0.0,  -1.4),    # add only if strand is self-complementary
    # 10 unique NN steps:
    "AA/TT":       (-7.9, -22.2),
    "AT/TA":       (-7.2, -20.4),
    "TA/AT":       (-7.2, -21.3),
    "CA/GT":       (-8.5, -22.7),
    "GT/CA":       (-8.4, -22.4),
    "CT/GA":       (-7.8, -21.0),
    "GA/CT":       (-8.2, -22.2),
    "CG/GC":      (-10.6, -27.2),
    "GC/CG":       (-9.8, -24.4),
    "GG/CC":       (-8.0, -19.9),
}
```

Steps not listed as keys (e.g. `TT/AA`, `TG/AC`) are obtained by reading the duplex from the *other* strand — i.e. reverse-complement the dinucleotide and look it up. (`TT/AA` ≡ `AA/TT`, `TG/AC` ≡ `CA/GT`, etc.) A correct implementation tries the key, and on a miss looks up the reverse-complement of the step.

### 3.3 The Tm formula (with R and salt correction)
Two-state model:

```
Tm (Kelvin) = (1000 · ΔH_total) / ( ΔS_total + R · ln(C_T / x) )
Tm (°C)     = Tm(K) − 273.15
```

- `ΔH_total` in kcal/mol → multiply by 1000 to match ΔS in cal/(mol·K).
- **R = 1.987 cal/(mol·K)** (gas constant in these units).
- `C_T` = total strand concentration (mol/L). For non-self-complementary strands in excess of one component, `x = 4` (use `C_T/4`); for self-complementary strands `x = 1` (use `C_T`). In origami, staple ≫ scaffold, so the standard convention is to use the staple concentration with `x = 4`. A typical staple concentration is ~100 nM (Aksel 2024 used 100 nM staples, 10:1 over scaffold).

**Salt correction (SantaLucia 1998, entropy form — the recommended default):**

```
ΔS_corrected = ΔS_total + 0.368 · (N − 1) · ln[Na+]
```

where `N` = number of nucleotides in the duplex (so `N−1` = number of phosphates / NN steps), and `[Na+]` is the **total monovalent-equivalent cation concentration in mol/L**. Origami buffers are Mg2+-based (typically 10–20 mM MgCl2 in TAE-Mg); convert to a monovalent equivalent (a common rule of thumb is [Na+]_eq ≈ 120·√[Mg2+], from the Owczarzy 2008 correction) or apply a dedicated divalent correction. The simplest defensible default for a v0 compiler: use the SantaLucia monovalent salt correction with an effective [Na+] tuned so predicted T_fold matches a measured calibration anneal.

This whole block is ~40 lines of Python and matches Biopython `Tm_NN(seq, nn_table=DNA_NN3, saltcorr=5)`.

---

## 4. The concrete, implementable yield-optimization algorithm

Given a **fixed scaffold routing** (e.g. a caDNAno design with the scaffold path and the set of candidate phosphate "break points"), choose where to break the staple strands. This mirrors Aksel 2024 / pyOrigamiBreak but is restated so our compiler can implement it from scratch.

### 4.1 Inputs
- Scaffold sequence (M13mp18 or synthetic) mapped onto the routing.
- The graph of **candidate break points** = every phosphate bond where a staple *could* be nicked, given lattice geometry and crossover positions.
- Target parameters: `T_fold_target` (e.g. 50–55 °C), allowed staple length window `[Lmin, Lmax]` (e.g. 21–50 nt), max crossovers per staple `Xmax` (e.g. 2), buffer salt, strand concentration.

### 4.2 Objective (score a *candidate staple set* S; lower = better)
```
Score(S) = w1 · Σ_s  (T_fold(s) − T_fold_target)^2          # Tm window (Sec 3) — cooperativity
         + w2 · Σ_s  loop_penalty(s)                          # crossovers/loop-closure entropy
         + w3 · Σ_s  length_penalty(s)                        # outside [Lmin,Lmax]
         + w4 · repeat_penalty(S)                             # repeated k-mers across all staples
         + w5 · Σ_s  hairpin_penalty(s)                       # self-complementarity / secondary structure
         + w6 · Σ_s  polyrun_penalty(s)                       # ≥4 G (Gquad) or ≥5 A/T runs
```

Concrete definitions of each term (all codeable today):

1. **Tm term** — `T_fold(s)` from Section 3 (NN Tm, salt-corrected). Penalize squared deviation from the window center; this *clusters* every staple's folding temperature so the set anneals cooperatively. (Equivalently penalize only deviations outside [T_lo, T_hi].)

2. **Loop-closure / crossover term** — count crossovers `c(s)` (= scaffold loop closures) the staple makes. Penalty grows with `c(s)`; in Aksel's formulation each loop closure adds an entropic `ΔG_loop` ≈ `−T·ΔS_loop` where `ΔS_loop ≈ −R·[ (3/2)·ln(n) + ... ]` for a Jacobson–Stockmayer loop of `n` scaffold bases (n = bases enclosed between the two crossover feet). Simplest codeable proxy: `loop_penalty(s) = α·c(s) + β·Σ_loops ln(n_loop)`. **Weight this heavily (w2 large):** the headline finding is that crossover count dominates raw binding length.

3. **Length term** — `0` inside `[Lmin,Lmax]`, quadratic outside. Encourages the ~32–42 nt regime.

4. **Repeat term** — build a hash set of all k-mers (e.g. k = 8) across every staple's binding domain; penalty = number of k-mers occurring more than once (off-target binding risk, Section 1.4). This directly attacks the M13 repeat problem.

5. **Hairpin term** — for each staple, compute longest self-complementary stem (reverse-complement match with ≤ small loop); penalize stems longer than ~6 bp. (Cheap heuristic; an optional upgrade calls an external MFE folder such as ViennaRNA `RNAfold`/UNAFold-DNA or `seqfold` to get ΔG of secondary structure and penalize ΔG < threshold.)

6. **Poly-run term** — regex count of `G{4,}`, `C{4,}`, `A{5,}`, `T{5,}`; fixed penalty each.

### 4.3 Optimizer (two interchangeable backends)
- **Backend A — Shortest-path (exact, fast; this is what Aksel/pyOrigamiBreak do).** Reduce break-point selection to a weighted directed graph: nodes = candidate break points along a staple-strand path, edge from break i→j = "make one staple spanning i..j" with edge weight = that staple's local score (Tm + loop + length + hairpin + polyrun terms). The minimum-weight path that tiles the strand = optimal break set. Use **k-shortest-paths (k≈10)** to keep alternatives, then pick the global combination minimizing the full objective (the repeat term couples staples, so evaluate the cross-staple `repeat_penalty` over each candidate combination). This is deterministic and matches the proven method.
- **Backend B — Simulated annealing (flexible, handles the coupled repeat/hairpin terms natively).** State = a full set of break points. Moves = add/remove/shift a break (subject to lattice legality and length window). Accept worse states with probability `exp(−ΔScore / T)`; geometric cooling `T ← 0.95·T` from a `T0` set so ~80% of uphill moves accept initially, ~5,000–50,000 iterations. This is the "shape/staple annealing" family (Babatunde 2021) and trivially incorporates the non-decomposable `repeat_penalty(S)` and hairpin terms that the pure shortest-path can't see globally.

**Recommended v0:** shortest-path to get a strong seed, then a short simulated-annealing polish to optimize the cross-staple repeat/hairpin terms. Validate predicted T_fold uniformity by plotting the staple T_fold histogram (Aksel's "heatmap by T_fold" diagnostic).

### 4.4 Optional learned scoring model (clearly labeled experimental)
Replace the hand-weighted `Score(S)` with a learned `f_θ(features(S)) → predicted_yield`, trained on our own (design → measured-yield-from-TEM/gel) pairs. Features = the same physics terms above (T_fold distribution moments, crossover histogram, max repeat length, min hairpin ΔG, GC stats). Gradient-boosted trees or a small MLP suffice. **This is a north-star upgrade — there is no published model that does this well enough to ship as the default, so it must be marked experimental and the physics model remains the trustworthy baseline.**

---

## 5. The honest moat statement

What we can *truthfully* claim the software does:
1. Implements the published, lab-validated nearest-neighbor thermodynamics (SantaLucia) and the Aksel-2024 loop-closure-aware staple-break optimization that produced **6–30× measured yield gains**.
2. Adds repeat-, hairpin-, and poly-run penalties grounded in known origami failure modes.
3. Packages shape→routing→staple-recipe into one click with a T_fold-uniformity diagnostic.

What we must NOT claim:
- That it's a deep-learning "AI" designing sequences from scratch (it's physics + classical optimization).
- That a learned yield predictor is validated (it isn't; it's an experimental add-on).
- Any yield number beyond what we ourselves measure or what the cited papers measured.

The moat is **integration + correct physics + the loop-closure insight most tools omit**, not a proprietary neural net.

---

## 6. Citations (all verified to exist via web search)

1. **SantaLucia, J. Jr. (1998).** "A unified view of polymer, dumbbell, and oligonucleotide DNA nearest-neighbor thermodynamics." *PNAS* 95(4):1460–1465. DOI: 10.1073/pnas.95.4.1460. https://www.pnas.org/doi/abs/10.1073/pnas.95.4.1460 — *Tm/NN parameters.* (Theory/empirical thermodynamics; demonstrated experimentally for oligo melting.)
2. **Allawi, H.T. & SantaLucia, J. Jr. (1997).** "Thermodynamics and NMR of internal G·T mismatches in DNA." *Biochemistry* 36(34):10581–10594. DOI: 10.1021/bi962590c — *source of the unified Watson–Crick NN values (Biopython DNA_NN3).*
3. **SantaLucia, J. Jr. & Hicks, D. (2004).** "The thermodynamics of DNA structural motifs." *Annu. Rev. Biophys. Biomol. Struct.* 33:415–440. DOI: 10.1146/annurev.biophys.32.110601.141800. https://www.annualreviews.org/doi/10.1146/annurev.biophys.32.110601.141800 — *review consolidating NN parameters + salt corrections.*
4. **Rothemund, P.W.K. (2006).** "Folding DNA to create nanoscale shapes and patterns." *Nature* 440:297–302. DOI: 10.1038/nature04586. https://www.nature.com/articles/nature04586 — *the origami method (lab-demonstrated, ~100 nm shapes).*
5. **Douglas, S.M.; Marblestone, A.H.; Teerapittayanon, S.; Vazquez, A.; Church, G.M.; Shih, W.M. (2009).** "Rapid prototyping of 3D DNA-origami shapes with caDNAno." *Nucleic Acids Research* 37(15):5001–5006. DOI: 10.1093/nar/gkp436. https://academic.oup.com/nar/article/37/15/5001/2409858 — *the standard scaffold-routing CAD tool / staple-length regime (lab-demonstrated designs).*
6. **Aksel, T.; et al. / Douglas lab (2024).** "Design principles for accurate folding of DNA origami." *PNAS* 121(48):e2406769121. DOI: 10.1073/pnas.2406769121. https://www.pnas.org/doi/10.1073/pnas.2406769121 (PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC11621765/) — *loop-closure-aware staple-break optimization; 6–30× measured yield gains (gel + TEM). Code: github.com/douglaslab/pyOrigamiBreak. **Demonstrated experimentally.***
7. **Sobczak, J.-P.J.; Martin, T.G.; Gerling, T.; Dietz, H. (2012).** "Rapid folding of DNA into nanoscale shapes at constant temperature." *Science* 338(6113):1458–1461. DOI: 10.1126/science.1229919. https://www.science.org/doi/10.1126/science.1229919 — *isothermal folding at T_fold; basis for Tm-balancing rationale (lab-demonstrated).*
8. **Babatunde, B.; Arias, D.S.; Cagan, J.; Taylor, R.E. (2021).** "Generating DNA Origami Nanostructures through Shape Annealing." *Applied Sciences* 11(7):2950. DOI: 10.3390/app11072950. https://www.mdpi.com/2076-3417/11/7/2950 — *simulated-annealing + shape-grammar scaffold routing (computational only).*
9. **Owczarzy, R.; et al. (2008).** "Predicting stability of DNA duplexes in solutions containing magnesium and monovalent cations." *Biochemistry* 47(19):5336–5353. DOI: 10.1021/bi702363u — *Mg2+ → monovalent-equivalent salt correction for origami buffers.*
10. **ML-for-characterization (context, not sequence design):** YOLOv5 DNA-origami detection — *Nanoscale Advances* / related (2022), PMC8907326, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8907326/; and CNN ligation-number characterization, arXiv:2503.10950. *Demonstrates "ML in DNA origami" is image analysis, not staple design.*

---

## 7. Code facts (for the software compiler)

- **Tm:** `Tm(K) = 1000·ΔH / (ΔS + R·ln(C_T/x)); Tm(°C) = Tm(K) − 273.15`. **R = 1.987 cal/(mol·K)**, `x = 4` (non-self-comp, staple in excess) or `1` (self-comp).
- **NN params:** SantaLucia-unified set = Biopython `Bio.SeqUtils.MeltingTemp.DNA_NN3` (table in §3.2). Reverse-complement lookup for missing dinucleotide keys.
- **Init terms:** `init_A/T = (2.3, 4.1)`, `init_G/C = (0.1, −2.8)` applied per terminal base pair; `sym = (0, −1.4)` only if self-complementary.
- **Salt correction (default):** `ΔS += 0.368·(N−1)·ln[Na+]` (entropy form, SantaLucia 1998 = Biopython `saltcorr=5`). For Mg2+ origami buffers use Owczarzy 2008 monovalent-equivalent or calibrate effective [Na+].
- **Tooling:** `pip install biopython` (Tm via `MeltingTemp.Tm_NN`); optional secondary-structure ΔG via `pip install seqfold` or ViennaRNA `RNAfold`/UNAFold (DNA params). Input/output format: **caDNAno JSON** (the de-facto origami exchange format); reference optimizer **github.com/douglaslab/pyOrigamiBreak** (Python).
- **Objective terms:** `w1·Σ(T_fold−target)²  +  w2·loop/crossover penalty (α·c + β·Σln(n_loop))  +  w3·length-window penalty  +  w4·repeated-k-mer count (k=8)  +  w5·hairpin/self-comp stem penalty  +  w6·poly-run penalty (G≥4, C≥4, A≥5, T≥5)`. Weight w2 (crossover/loop) highest per Aksel 2024.
- **Optimizers:** k-shortest-paths (k≈10) over the break-point graph (deterministic, matches pyOrigamiBreak) AND/OR simulated annealing (geometric cooling 0.95, 5k–50k iters) to handle coupled repeat/hairpin terms. Recommended: shortest-path seed + SA polish.
- **Diagnostic:** plot per-staple T_fold histogram; tight unimodal distribution near target ⇒ cooperative high-yield anneal.
- **Parts:** none — this is a pure-software layer.
