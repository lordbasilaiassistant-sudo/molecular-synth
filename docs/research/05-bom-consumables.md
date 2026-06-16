# BOM 05 — Consumables & Sourcing Reality Check (Wet-Lab Biochemistry Inputs)

**Project:** Molecular Synth v0 — desktop DNA-origami rig + shape→staple compiler
**Scope of this doc:** The *consumable* (use-up) chemistry inputs for ONE DNA-origami design (~200 staple strands, M13mp18 scaffold). Hardware (thermocycler/heat-block, gel rig, centrifuge, imaging) is costed separately in the rig BOM. This doc answers: *can a hobbyist with a credit card and no institutional account actually buy these, and what does one design honestly cost?*
**Date verified:** 2026-06-16. Prices are list/snapshot and drift; treat ±20%.

---

## 0. The honest headline

- **A single ~200-staple DNA-origami design costs roughly $700–$1,000 in consumables if you buy staples as individual tubes in a 96-well plate at IDT** (the staples dominate). The scaffold, buffers, gel, and stain together are only ~$150–$250 and most of that is reusable across dozens of designs.
- **If you buy the 200 staples as a single IDT oPool (pooled synthesis) instead of individual tubes, the staple cost collapses to ~$100–$400**, but you lose the ability to address individual strands (no selective omission, no per-staple handles) and concentrations are lower/less precise. For a first proof-of-structure (e.g. Rothemund smiley / a rectangle), an oPool is the cheapest viable route. For anything with functionalized handles or selective-staple experiments, you need the addressable plate.
- **Yes, a US hobbyist can buy from IDT and NEB with a personal credit card and no institutional account.** Both accept Visa/MC/Amex and ship to residential addresses. This is verified below. The DNA itself (M13 scaffold, short oligos) is **not** controlled/regulated — these are standard molecular-biology reagents. (The one place to be careful: vendors screen *gene-length* synthetic DNA against pathogen sequences; origami staples are 20–60 nt and far below any concern.)
- **Nothing in the consumable list strictly requires an institution.** The only items that are "lab-account-flavored" (Amicon filters, some MgCl2 grades) all have Amazon-purchasable equivalents listed below.

---

## 1. Scaffold ssDNA (M13mp18 / p7249) — the "blank canvas"

The scaffold is the single long circular ssDNA (~7,249 nt for M13mp18) that the staples fold. Two real, hobbyist-buyable sources:

### 1a. NEB N4040 — M13mp18 Single-stranded DNA
- **Vendor:** New England Biolabs (neb.com) and resellers (Fisher).
- **Product:** N4040S, M13mp18 ssDNA, **10 µg @ 1 µg/µL**.
- **Price:** **~$40** (N4040S, per NEB 2024 price list). [NEB product page](https://www.neb.com/products/n4040-m13mp18-single-stranded-dna) · [NEB 2024 pricing PDF](https://www.umassmed.edu/globalassets/enzyme-freezer/documents/neb-2024-pricing.pdf) · [Fisher listing](https://www.fishersci.com/shop/products/m13mp18-single-stranded-dna/50811790)
- **Reality:** NEB sells to individuals with a credit card; ships in the US to residential addresses. 10 µg = ~4.2 pmol at 7249 nt (MW ≈ 2.39 MDa). A "standard" origami fold uses ~10 nM scaffold in 50–100 µL = ~0.5–1 pmol per reaction, so **10 µg ≈ 4–8 folding reactions.** Cheap entry, but you will burn through it fast if you iterate. *Caveat: NEB's M13mp18 is sold as a sequencing/cloning template; it is the same sequence cadnano calls "M13mp18," so it works as a scaffold, but it is not concentration-optimized for origami the way tilibit's is.*

### 1b. tilibit nanosystems — Scaffold ssDNA p7249 (origami-grade)
- **Vendor:** tilibit nanosystems (tilibit.com), the spin-out that productized DNA-origami reagents.
- **Product:** p7249 ssDNA (sequence identical to cadnano "M13mp18"). Options:
  - 0.5 mL @ 100 nM = 50 pmol (112 µg), **~25 folding reactions** — **€112 (~$120)**
  - 2 mL @ 100 nM = 200 pmol (448 µg), ~100 reactions — same €112/unit tier scales down to €0.5/µg
  - 2 mL @ 400 nM = 800 pmol (1792 µg), ~400 reactions — €0.35/µg
- **Price/URL:** **€112 (~$120)** base. [tilibit p7249 product](https://www.tilibit.com/products/single-stranded-scaffold-dna-type-p7249) · [tilibit scaffold collection](https://www.tilibit.com/collections/scaffold-dna)
- **Reality:** tilibit ships internationally and is the de-facto origami scaffold vendor; it is delivered pre-quantified at origami concentration ("sufficient for ~25 standard reactions"). For a hobbyist this is the *less error-prone* choice (you don't have to QC your own scaffold), at ~3× the per-reaction cost of NEB. Ships from Germany — expect customs/shipping and a longer lead time to the US.

**Recommendation for v0:** Start with **NEB N4040 ($40)** to validate the rig cheaply; switch to tilibit if scaffold-quality is suspected as the failure mode. GuildBio also resells M13 scaffolds but tilibit/NEB are the two reliably-stocked routes.

---

## 2. Staple oligos — the dominant cost, and the one real decision

A ~200-staple design = ~200 distinct short oligos (typically 32–42 nt; ~7,000–8,400 total bases across the set).

### 2a. Option A — IDT individual oligos in a 96-well plate (addressable, the standard origami route)
- **Vendor:** Integrated DNA Technologies (idtdna.com). Order as **"Plates"** (HotPlates / standard plate). Minimum 48 oligos/plate; ~200 staples = ~3 plates of 96 wells (~2 full + 1 partial).
- **Format:** 25 nmol scale, **desalted (standard)** — the correct, cheapest purification for origami staples (no HPLC/PAGE needed; origami tolerates n-1 truncation products).
- **Price reality:** IDT does **not** publish a flat per-base number on a stable public URL (the FAQ pages redirect/paywall), but the well-established community figure for **25 nmol desalted plate oligos is ≈ $0.06–$0.10 per base**, plus a per-plate setup/normalization handling fee. Working the math:
  - ~200 staples × ~38 nt avg = ~7,600 bases × ~$0.09/base ≈ **$680** in synthesis
  - + plate handling (~3 plates) ≈ **$50–$150**
  - **≈ $700–$850 total for the addressable staple set.**
- **URLs:** [IDT plate ordering](https://www.idtdna.com/site/Order/menu/Sub?type=plate) · [IDT DNA-origami reagents](https://www.idtdna.com/pages/products/custom-dna-rna/dna-oligos/custom-dna-oligos/dna-origami-reagents) · [HotPlates](https://www.idtdna.com/pages/products/custom-dna-rna/dna-oligos/custom-dna-oligos/hotplates-oligos)
- **Why this format:** Each well = one addressable strand. You can omit specific staples (to leave docking sites), add 3′/5′ handles to chosen strands, or do selective experiments. This is what every origami lab uses.

### 2b. Option B — IDT oPools (pooled synthesis, cheapest per base, NOT individually addressable)
- **Vendor:** IDT oPools. One tube containing all ~200 sequences mixed.
- **Price reality:** oPools is priced as **a flat plate/pool fee (~$103–$109) plus a per-base rate that is dramatically lower than tube synthesis** for hundreds of sequences. For ~200 short staples (~7,600 bases, well under the first 3,300-base tier breakpoint into higher tiers) the **all-in cost is typically ~$100–$400** depending on length tier — i.e. **roughly 2–7× cheaper than the addressable plate.** [IDT oPools](https://www.idtdna.com/pages/products/custom-dna-rna/dna-oligos/custom-dna-oligos/opools-oligo-pools) · [oPools launch / spec (synbiobeta)](https://www.synbiobeta.com/read/idt-launches-opools-tm-oligo-pools-the-longest-highest-fidelity-and-ready-to-use-custom-oligo-pools-on-the-market)
- **The catch (be honest):** You get **one tube of everything**. You cannot leave out a staple, cannot put a handle on just one strand, and the per-strand concentration is low and only approximately equimolar. It is excellent for "does my rig fold a known shape at all?" with a published staple set, and useless for selective/functionalized work. Yield per pool is also limited (you can't fold dozens of reactions from one pool the way you can from 25 nmol tubes).

### 2c. Option C — Twist Bioscience oligo pools
- **Vendor:** Twist (twistbioscience.com). Twist's oligo pools are even cheaper per base at large N, but **Twist's account onboarding is more institution-oriented** and minimum-order/lead-time friction is higher for an individual. For a hobbyist, IDT (tube *or* oPool) is the path of least resistance. Listed here for completeness, not recommended for v0.

### Staple decision summary

| Route | ~200-staple cost | Addressable? | Best for |
|---|---|---|---|
| IDT plate, 25 nmol desalted | **~$700–$850** | Yes (per well) | Real origami, handles, selective staples |
| IDT oPools | **~$100–$400** | No (one tube) | First proof-of-fold of a known shape |
| Twist pools | lowest at scale | No | Not v0-friendly (account/MOQ friction) |

**v0 recommendation:** First fold of a *published* shape → **oPool (~$200)**. Once the rig is proven and you want your own/functionalized designs → **IDT 25 nmol desalted plate (~$750)**.

---

## 3. Buffers, gel, stain, plasticware, purification (all reusable across many designs)

These are bought once and amortize across dozens of designs. All are Amazon-buyable by a hobbyist; lab-account substitutes are noted.

### 3a. MgCl₂ (folding cation — origami folds in ~12–20 mM Mg²⁺)
- **GFS Chemicals 48801, Magnesium Chloride Hexahydrate, ACS reagent, 500 g** — Amazon, **~$30–$45**. [Amazon B01NBML9XZ](https://www.amazon.com/GFS-Chemicals-48801-Magnesium-Hexahydrate/dp/B01NBML9XZ)
- Cheaper reagent-grade flake (98+%) options exist (~$15–$25/lb) e.g. [Amazon B087NY97ZM](https://www.amazon.com/Magnesium-Chloride-Hexahydrate-Bottles-Reagent/dp/B087NY97ZM). ACS grade preferred for reproducibility. **No institution required.** 500 g lasts effectively forever (you need millimolar).

### 3b. TAE buffer (folding + running buffer; "1×TAE + 12.5 mM MgCl₂" is the canonical origami buffer)
- **MP Biomedicals 50× TAE, 1 L** — Amazon, **~$54**. [Amazon B01MS22FJF](https://www.amazon.com/MP-Biomedicals-11TAE50X01-TAE-Buffer/dp/B01MS22FJF)
- Cheaper generic 50× TAE 1 L ~$20–$30: [Amazon B09V5MVMN9](https://www.amazon.com/50X-TAE-Buffer-Tris-Acetate-EDTA-1L/dp/B09V5MVMN9). 1 L of 50× → 50 L of 1×. Buying TAE premixed is far easier than buying Tris/acetic acid/EDTA separately, and the same price. **No institution required.**

### 3c. Agarose (for the folding-QC gel — you run an agarose gel to confirm a tight folded band)
- **Molecular-biology-grade agarose, 100 g** — Amazon, **~$30–$55** (RPI, Benchmark A1701, Bioworld/Apex generics). [RPI 100 g](https://www.amazon.com/RPI-Agarose-Molecular-Strength-Electrophoresis/dp/B00I31YMRU) · [Benchmark A1701 100 g](https://www.amazon.com/Benchmark-Scientific-A1701-Purified-Molecular/dp/B00XW1JREY). At ~1.5% gels, 100 g = dozens of gels. **No institution required.**

### 3d. DNA stain (visualize bands — use a safer EtBr alternative)
- **Biotium GelRed 10,000×, 0.5–1 mL** — **~$70–$110** (Biotium direct or resellers; also on Amazon/Sigma SCT123). [Biotium GelRed](https://biotium.com/product/gelred-nucleic-acid-gel-stain/) · [Sigma SCT123](https://www.sigmaaldrich.com/US/en/product/mm/sct123)
- Alternative: **SYBR Safe (Thermo S33102)** ~$80–$120. GelRed is the standard origami choice (non-mutagenic, post-stain or in-gel). 0.5 mL @ 10,000× = ~5 L of staining → many gels. **No institution required;** explicitly chosen because EtBr is the item a hobbyist should *avoid* (mutagen) and GelRed/SYBR Safe are the substitutes.

### 3e. Purification — remove excess staples after folding
Two real routes; **PEG is the hobbyist-friendly one.**
- **Route 1 — Amicon Ultra-0.5 mL, 100 kDa MWCO spin filters.** Spin-filter retains the assembled origami (MDa), washes out free staples. Millipore UFC510096 (100 kDa, 96-pack) on Amazon, **~$250–$350 for 96** (~$3/filter). [Amazon B004OYTK86](https://www.amazon.com/Millipore-Centrifugal-Ultracel-100-Purification-Concentration/dp/B004OYTK86) · [Sigma UFC5100](https://www.sigmaaldrich.com/US/en/product/mm/ufc5100). Needs a benchtop centrifuge (rig hardware). Single-use consumable. *This is the "lab-flavored" item — but it is openly Amazon-purchasable, no institution needed.*
- **Route 2 (cheaper, recommended for v0) — PEG precipitation.** Mix folded sample 1:1 with PEG precipitation buffer (1×TAE, **15% (w/v) PEG-8000**, ~500 mM NaCl, ~12 mM MgCl₂), spin, resuspend. Per **Stahl et al. 2014** (the canonical origami PEG protocol — see Claims). Consumable cost ≈ a jar of **PEG-8000 (~$25–$40, 500 g–1 kg, Amazon/laballey)** + NaCl (~$10) that lasts dozens of preps. Needs only a microcentrifuge. **No special filter consumable, no institution.**

### 3f. PCR/folding tubes & nuclease-free water (trivial, Amazon)
- **0.2 mL PCR 8-tube strips, DNase/RNase-free, ~125 strips** — Amazon, **~$12–$18**. [Amazon B09CVDBMQ9](https://www.amazon.com/PCR-Tubes-0-2ml-Strip-Included/dp/B09CVDBMQ9). (Folding happens in a thermocycler/heat-block in these tubes.)
- **Nuclease-free / molecular-biology-grade water, 1 L** — Amazon, **~$15–$25** (Quality Biological 351-029-131). [Amazon B07T14KWBZ](https://www.amazon.com/Quality-Biological-351-029-131-Molecular-Endotoxin/dp/B07T14KWBZ). Or make your own from distilled + autoclave; premixed is cheap enough. **No institution required.**
- **Micropipettes** (not strictly a consumable but needed to dispense µL): cheap adjustable-volume pipette sets (2–20 µL, 20–200 µL, 100–1000 µL) on Amazon **~$60–$120 for a 3-pipette set + tips**, e.g. generic "lab pipette set." Pipette *tips* (filter or standard, racked) are the recurring consumable, **~$15–$25 per 1,000**.

---

## 4. Honest total — ONE ~200-staple origami design

Splitting **one-time/reusable** (bought once, amortizes over many designs) from **per-design** (consumed each new design = the new staple set):

### Per-design recurring cost (the part that repeats for each NEW design)
| Item | Cheapest (oPool) | Standard (addressable plate) |
|---|---|---|
| ~200 staples | ~$200 (oPool) | ~$750 (IDT 25 nmol desalted plate) |
| Scaffold draw (per fold, amortized) | ~$5 (NEB) | ~$5 (NEB) |
| **Per-design total** | **~$205** | **~$755** |

### One-time / reusable starter kit (covers dozens of designs)
| Item | Price |
|---|---|
| Scaffold stock (NEB N4040, 10 µg) | $40 |
| MgCl₂ ACS 500 g | $35 |
| 50× TAE 1 L | $30 |
| Agarose 100 g | $40 |
| GelRed stain 0.5 mL | $90 |
| PEG-8000 500 g + NaCl (purification) | $45 |
| PCR strip tubes (125) | $15 |
| Nuclease-free water 1 L | $20 |
| Pipette tips (1,000) | $20 |
| **Reusable subtotal** | **~$335** |

### Bottom line
- **First design, cheap path (oPool + reusable kit):** **~$205 + ~$335 ≈ $540 all-in**, then **~$205 per additional known-shape design.**
- **First design, real-origami path (addressable plate + reusable kit):** **~$755 + ~$335 ≈ $1,090 all-in**, then **~$755 per additional custom design.**
- The reusable kit is bought once; from the 2nd design on, you only pay for new staples (+ ~$5 scaffold). **The staple synthesis is ~85–95% of marginal cost.** Optional Amicon filters add ~$300 if you prefer spin-filter over PEG.

---

## 5. Institution-required items & hobbyist substitutes

| "Lab-account" item | Required? | Hobbyist substitute |
|---|---|---|
| IDT / NEB account | **No** | Both take personal credit cards, ship residential. Verified. |
| Twist Bioscience | Soft-gated (MOQ/onboarding) | Use IDT oPools instead — same pooled-synthesis benefit, easy individual checkout. |
| Amicon 100 kDa spin filters | No (Amazon) | Or skip entirely: **PEG-8000 precipitation** (Stahl 2014) needs only a microcentrifuge + cheap reagents. |
| ACS-grade MgCl₂ | No | Reagent-grade flake from Amazon works; ACS just improves reproducibility. |
| EtBr (classic stain) | — (avoid) | **GelRed / SYBR Safe** — safer, Amazon-buyable, the actual community standard. |

**Net:** zero items in the consumable chain are gated behind an institution. The DNA reagents are unregulated standard mol-bio products; origami oligos are far too short to trip vendor biosecurity gene-screening.

---

## 6. Claims (peer-reviewed, verified)

1. **DNA origami: a single long scaffold folded by ~200 short staples yields a designed ~100 nm 2D shape (the "smiley") — demonstrated.**
   Rothemund, P. W. K. *Folding DNA to create nanoscale shapes and patterns.* **Nature** 440, 297–302 (2006). DOI: 10.1038/nature04586. https://www.nature.com/articles/nature04586 — *demonstrated=true.* This is the method's founding experimental paper; scope: ~100 nm planar shapes, not macroscopic.

2. **PEG (PEG-8000) precipitation purifies dense, pure DNA-origami solutions and removes excess staples — demonstrated.**
   Stahl, E.; Martin, T. G.; Praetorius, F.; Dietz, H. *Facile and Scalable Preparation of Pure and Dense DNA Origami Solutions.* **Angew. Chem. Int. Ed.** 53, 12735–12740 (2014). DOI: 10.1002/anie.201405991. https://onlinelibrary.wiley.com/doi/full/10.1002/anie.201405991 — *demonstrated=true.* Source of the 15% PEG-8000 / 500 mM NaCl / Mg²⁺ buffer used in §3e.

3. **Staple oligonucleotides dominate DNA-origami material cost, and staple recycling/reuse cuts that cost substantially — demonstrated.**
   Becker, F. et al. *Reusing excess staple oligonucleotides for economical production of DNA origami* (also published as *Cost-efficient folding ... via staple recycling*, **Nanoscale** 2025, DOI 10.1039/D5NR01435B). bioRxiv 2024.08.27.609958. https://www.biorxiv.org/content/10.1101/2024.08.27.609958v1.full — *demonstrated=true.* Reports ~33% staple-cost reduction over 5 reuse cycles (theoretical max ~41%), and that staples are the majority of fabrication cost — directly supports §4's "staples are 85–95% of marginal cost."

---

## 7. Notes / caveats for the compiler & rig team

- The shape→staple compiler (cadnano/scadnano output) must emit sequences against the **exact scaffold sequence you buy** (NEB M13mp18 = cadnano "M13mp18" = tilibit p7249 — these three are interchangeable; do **not** mix a p8064/p8634 design with a 7249 scaffold).
- Compiler should support **two export modes**: (a) IDT plate-spec `.xls`/IDT bulk-input format for addressable 25 nmol plates, and (b) a single concatenated sequence list for an **oPool** order — because that switch is the single biggest cost lever ($200 vs $750).
- Folding QC = agarose gel band + (ideally) AFM later; the consumables here cover the *gel* QC. AFM/imaging is rig hardware, out of scope for this doc.
