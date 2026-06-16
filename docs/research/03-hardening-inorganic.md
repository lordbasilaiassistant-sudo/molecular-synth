# 03 — Hardening the Soft DNA Template into a HARD Inorganic Structure

**Project:** Molecular Synth v0 — desktop DNA-origami nanofab rig
**This module:** turning the floppy, water-soluble DNA-origami "master pattern" into a rigid, robust inorganic replica (silica, metal oxide, or solid metal).
**Date:** 2026-06-16
**Scope honesty up front:** Everything here makes structures in the **~10 nm – 1 µm** range. Nothing here makes a macroscopic object. Drexler-style diamondoid mechanosynthesis is NOT in this document and is NOT demonstrated — it is north-star/simulation-only. What IS demonstrated and reproducible is *templated inorganic transcription* of a DNA shape into a hard material.

---

## Why harden at all?

A bare DNA-origami object is:
- only stable in **high-Mg²⁺ / high-salt** buffer (falls apart in low salt, pure water, or biological fluid),
- mechanically floppy (persistence length of dsDNA ~50 nm; origami is a soft hydrogel-like solid),
- degraded by nucleases and by drying (collapses under capillary forces / TEM vacuum without stabilization).

Hardening converts the DNA from "the product" into "the **template/mold**." After hardening you can dry it, image it in vacuum SEM/TEM, etch with it, or use it as a real material. This is the single most important step that turns a DNA-origami hobby into a *nanomanufacturing* rig.

There are three demonstrated routes, in increasing equipment cost:

1. **Sol–gel silicification** (DNA → SiO₂ shell) — **DIY-feasible in a tube.** ← primary route for this build
2. **Metal casting in DNA molds** (DNA cavity → solid Au/Ag) — DIY-feasible chemistry, harder QC
3. **Atomic layer deposition (ALD)** (DNA → conformal TiO₂/ZnO/Al₂O₃) — **NOT a home build**; needs a vacuum ALD reactor. Mark optional / fab-service-only.

---

## ROUTE 1 — Sol–gel silicification (PRIMARY, DIY-feasible)

### How it works (chemistry)
The DNA backbone is polyanionic (negatively charged phosphates). You electrostatically recruit a **positively charged aminosilane** to the DNA surface, which then acts as a nucleation layer for **silica condensation** from a tetraalkyl-orthosilicate precursor (TEOS or TMOS). Sol–gel hydrolysis/condensation grows a conformal SiO₂ skin that locks the shape in place.

Two reagent recipes appear in the literature:

- **Liu et al. 2018 (Yan lab, ASU) — "DNA-origami silicification (DOS)":** uses **TMAPS** (N-trimethoxysilylpropyl-N,N,N-trimethylammonium chloride, a *cationic* aminosilane) as the nucleator + **TEOS** as the silica source. Optimal window: **TMAPS 2.0–2.5%, TEOS ~2.0%** (their own data: <2.0% TMAPS → incomplete, can't outcompete Mg²⁺; >2.5% → free nucleation in solution; TEOS plateaus 2–6%, self-aggregates >7%).
- **Nguyen / Heuer-Jungemann et al. 2019 (Liedl lab):** sol–gel growth of a controllable silica shell whose thickness is tuned by precursor concentration and time; APTES-type aminosilane chemistry is the same family.

Both are run **in a microcentrifuge tube, at room temperature, no vacuum, no special atmosphere.** That is exactly what makes this the home route.

### Demonstrations (REAL, peer-reviewed)

| # | Claim | Paper | Demonstrated? | Scope |
|---|-------|-------|---------------|-------|
| 1.1 | DNA origami can be faithfully coated/converted into a silica composite that replicates 1D/2D/3D shapes | Liu, Zhang, Jing, Yan et al., *Nature* **559**, 593–598 (2018), DOI 10.1038/s41586-018-0332-7 | **TRUE** | features **10–1000 nm**; frame, curved, porous origami; ~3 nm fidelity; mechanical stiffness increased ~10× |
| 1.2 | A protective silica shell of controllable thickness can be grown on DNA origami by sol–gel chemistry, preserving structural integrity | Nguyen, Döblinger, Liedl, Heuer-Jungemann, *Angew. Chem. Int. Ed.* **58**(3), 912–916 (2019), DOI 10.1002/anie.201811323 | **TRUE** | nm-thick conformal shell, EDX-confirmed uniform Si; thickness tuned by precursor conc. + time |
| 1.3 | Step-by-step reproducible protocol (DOS) for solidifying framework nucleic acids with silica | Jing, Zhang, Liu, Yan et al., *Nature Protocols* **14**, 2416–2436 (2019), DOI 10.1038/s41596-019-0184-0 | **TRUE** | ~3 nm precision, 10 → >1000 nm; gives exact TMAPS/TEOS %/timing |

**This is the route the rig should target.** It is the only inorganic-hardening route that is genuinely a tube + reagents + bench centrifuge job.

### What it does NOT do (honest limits)
- Output is **SiO₂ (glass), not a metal and not diamond.** Good for rigidity, imaging, etch-masking; not conductive.
- Shell adds a few nm — sub-5 nm features blur slightly.
- Still nanoscale only. A silicified origami "gear" is ~100 nm; it is not a watch part.

---

## ROUTE 2 — Metal casting with DNA molds (DIY-feasible chemistry, harder QC)

### How it works
Design a 3D DNA-origami "mold" with an internal **cavity** of a defined shape, place a small **gold seed** nanoparticle inside, then grow the seed (reduce Au³⁺ or Ag⁺ from solution onto the seed) until the metal fills the cavity and casts the shape. The DNA wall confines growth.

### Demonstrations (REAL, peer-reviewed)

| # | Claim | Paper | Demonstrated? | Scope |
|---|-------|-------|---------------|-------|
| 2.1 | A rigid DNA mold + nucleating gold seed casts user-specified 3D inorganic (Ag/Au) nanostructures at ~3 nm resolution | Sun, Boulais, Yin et al., *Science* **346**, 1258361 (2014), DOI 10.1126/science.1258361 | **TRUE** | silver cuboids w/ 3 independently tunable dims; Ag & Au; ~3 nm res; plasmonic props matched EM sim |
| 2.2 | 3D DNA-origami molds with internal cavities cast shape-controlled gold nanostructures | Helmi, Ziegler, Schiffels, Liedl, *Nano Lett.* **14**(11), 6693–6698 (2014), DOI 10.1021/nl503441v | **TRUE** | ~40 nm rod-like Au, square cross-section; higher-order assembly via DNA shell |

### DIY feasibility — caveats
- **Chemistry is benchtop:** seed-mediated Au/Ag growth (HAuCl₄ or AgNO₃ + mild reductant like hydroxylamine/ascorbate) is a classic kitchen-chemistry-adjacent reaction, no vacuum.
- **BUT:** designing a *closed cavity* mold and seeding it is much harder than coating an open shape. Yield is low; QC requires TEM you likely don't have at home. Treat metal casting as a **stretch/validation goal**, not the v0 deliverable.
- **Output:** actual solid metal (Au/Ag) nanostructures — conductive, plasmonic. This is the "coolest" route and the one with real photonics/biosensing value, but it is the least forgiving.

---

## ROUTE 3 — Atomic Layer Deposition (ALD) — OPTIONAL / FAB-SERVICE ONLY

### How it works
Vapor-phase, self-limiting alternating pulses of a metal precursor (e.g., TMA for Al₂O₃, TiCl₄/TDMAT for TiO₂, DEZ for ZnO) and an oxidant (H₂O/O₃) deposit a perfectly conformal, sub-nm-controlled oxide skin on the DNA. Produces the **highest-quality, thinnest, most uniform** hard coatings of any route.

### Demonstrations (REAL, peer-reviewed)

| # | Claim | Paper | Demonstrated? | Scope |
|---|-------|-------|---------------|-------|
| 3.1 | ALD Al₂O₃ (2–20 nm) stabilizes DNA nanostructure templates, preserving nanoscale features; used as imprint-lithography mask | Shen, Keller et al., *Beilstein J. Nanotechnol.* **8**, 2503–2510 (2017), DOI 10.3762/bjnano.8.236 | **TRUE** | DNA nanotubes & origami triangles; 2–20 nm Al₂O₃; survives UV/O₃ |
| 3.2 | Area-selective ALD of Al₂O₃/TiO₂/HfO₂ on 2D & 3D DNA nanostructures; used as hard mask for deep Si etch (antireflection) | Area-Selective ALD on DNA Nanostructures, *ACS Nano* **14**(7) (2020), DOI 10.1021/acsnano.0c04493 | **TRUE** | metal-oxide hard mask; Si deep-etch demo |
| 3.3 | Conformal ZnO/TiO₂/IrO₂ ALD inside µm-sized DNA-origami crystals → functional 3D nanoarchitectures | Fabrication of Functional 3D Nanoarchitectures via ALD on DNA Origami Crystals, *J. Am. Chem. Soc.* **147** (2025), DOI 10.1021/jacs.4c17232 (arXiv:2410.13393) | **TRUE** | needs critical-point drying + low-T ALD; ZnO/TiO₂/IrO₂ multilayers |

### Why this is NOT a $1500 home build
- Requires a **vacuum ALD reactor** (turbo/scroll pump, heated precursor lines, dosing valves, inert gas, exhaust scrubber). Lowest entry "benchtop" ALD systems start ~$30k–$80k.
- Hazardous precursors (TMA is pyrophoric; some are toxic). Not home-safe.
- Often needs **critical-point drying** beforehand to keep origami intact in vacuum — another specialized tool.

**Recommendation:** Mark ALD as **optional**. Path for a hobbyist who wants ALD-quality output: silicify at home (Route 1), then send pre-stabilized samples to a **university nanofab user-facility or a commerical ALD service** (e.g., a campus cleanroom, or services like those at shared nanofab centers) for the oxide coat. Do NOT budget an ALD reactor into the rig.

---

## DIY-feasibility verdict (decision for the build)

| Route | Equipment | Home-feasible? | Put in v0? |
|-------|-----------|----------------|------------|
| **1. Sol–gel silica** | tube, vortex, benchtop microcentrifuge, fume ventilation | **YES** | **YES — primary** |
| **2. Metal casting** | same + careful seed handling, ideally TEM for QC | partly (chemistry yes, QC hard) | stretch goal |
| **3. ALD oxide** | vacuum ALD reactor + CPD | **NO** | optional / external service |

The rig's hardening station = **a small fume-vented bench area, a vortex mixer, and a benchtop microcentrifuge**, plus the consumable silane reagents below. All already on the parts list for the wet-chem side of the rig.

---

## ORDERABLE PARTS (consumables — verified June 2026)

> All chemistry consumables; counted separately from the <$1500 rig hardware budget. US-purchasable.
> Aminosilanes & orthosilicates are **moisture-sensitive**; store sealed, dry. TEOS/TMOS and methanol-based TMAPS are flammable — handle with ventilation.

### Silica precursors (pick one; TEOS is cheapest & safest of the alkoxides)

| Reagent | Vendor | Size | Price | URL |
|---|---|---|---|---|
| **TEOS** (tetraethyl orthosilicate, ≥97%) | LabPro Inc (US) | 500 mL | **$41.92** | https://labproinc.com/products/tetraethyl-orthosilicate-500ml-t0100-500ml |
| TEOS, 98% | Sigma-Aldrich (Aldrich 86578 / 131903) | 250 mL–1 L | ~$60–120 (acct) | https://www.sigmaaldrich.com/US/en/product/aldrich/131903 |
| TEOS 98%, 100 mL | Thermo/Fisher AC157811000 | 100 mL | listed online | https://www.fishersci.com/shop/products/tetraethyl-orthosilicate-98-thermo-scientific/AC157811000 |
| TMOS (tetramethyl orthosilicate, faster-condensing alt.) | Thermo/Fisher AC203820250 | 25 g | listed online | https://www.fishersci.com/shop/products/tetramethyl-orthosilicate-99-thermo-scientific/AC203820250 |

**Note on TMOS vs TEOS:** TMOS hydrolyzes faster (more reactive) but releases methanol (more toxic) and is pricier in small sizes. **TEOS is the recommended DIY default** — cheaper, less toxic byproduct (ethanol), and is what most origami-silica protocols use. The LabPro 500 mL at ~$42 is the best hobbyist buy and ships in the US with no lab account.

### Aminosilane nucleator (need ONE of these)

| Reagent | Role | Vendor | Size | Price | URL |
|---|---|---|---|---|---|
| **TMAPS** (N-trimethoxysilylpropyl-N,N,N-trimethylammonium chloride, 50% in MeOH) — *cationic, used in Liu 2018 DOS recipe* | Charge-matched nucleator on DNA | Gelest SIT8415.0 | 100 g | acct pricing | https://www.gelest.com/product/SIT8415.0/ |
| TMAPS 50% in MeOH | same | Thermo/Fisher AAH6641414 | 25 g | listed online | https://www.fishersci.com/shop/products/n-3-trimethoxysilyl-propyl-n-n-n-trimethylammonium-chloride-50-methanol-thermo-scientific/AAH6641414 |
| **APTES** ((3-aminopropyl)triethoxysilane, ≥98%) — *amine nucleator, Liedl/Heuer-Jungemann family* | Amine nucleation layer | Sigma-Aldrich 741442 | 100 mL | **$178.36** | https://www.sigmaaldrich.com/US/en/product/aldrich/741442 |
| APTES, AR grade, CAS 919-30-2 | same | Amazon (3rd-party) | 100 mL | check listing | https://www.amazon.com/3-Aminopropyl-triethoxysilane-CAS-919-30-2-100ml/dp/B0DTP8RNLC |
| APTES, 99% | Thermo/Fisher 151080050 | 5 g | listed online | https://www.fishersci.com/shop/products/3-aminopropyltriethoxysilane-99-thermo-scientific/AC151080050 |

**Recipe guidance (from Liu 2018 / Jing 2019 Nat. Protoc.):** in the silicification reaction, **TMAPS 2.0–2.5% v/v** + **TEOS ~2.0% v/v** added to the Mg²⁺-buffered origami solution, mixed, and aged. APTES can substitute as the amine nucleator (Liedl-style). Start with TEOS + TMAPS to match the best-documented protocol; APTES is the easier-to-buy fallback.

### Metal-casting consumables (Route 2 — stretch goal only)

| Reagent | Role | Vendor | Size | Price | URL |
|---|---|---|---|---|---|
| **Gold(III) chloride trihydrate** HAuCl₄·3H₂O | Au source for seed growth | Sigma 520918 / Etsy resale | 1 g | ~$70–120 (Sigma); ~$60 Etsy | https://www.sigmaaldrich.com/US/en/product/aldrich/520918 |
| Silver nitrate AgNO₃ | Ag source (Sun 2014 cuboids) | widely available (photo/lab) | — | low | (commodity) |
| Hydroxylamine HCl / L-ascorbic acid | mild reductant for seeded growth | grocery/lab (ascorbate = vit C) | — | low | (commodity) |

> Au/Ag casting is a stretch goal; QC honestly needs TEM. Buy these only after silicification (Route 1) is working.

---

## What this module delivers to the rig

- **Hardening station = bench + vortex + microcentrifuge + ventilation** (no new big-ticket hardware).
- **Primary process:** TEOS + TMAPS (or APTES) sol–gel silicification, RT, in a tube → rigid SiO₂ replica of the origami, 10 nm–1 µm, ~3 nm fidelity. Fully demonstrated (Liu 2018, Nguyen 2019, Jing 2019).
- **Stretch:** Au/Ag mold casting (Sun 2014, Helmi 2014) — demonstrated science, harder QC.
- **Out of scope for home:** ALD oxide (Shen 2017, ACS Nano 2020, JACS 2025) — real & powerful, but vacuum-reactor-only; route to an external nanofab service if needed.
- **Hard ceiling, stated plainly:** nanoscale only. No macroscopic objects, no diamondoid. Diamondoid mechanosynthesis = north-star, simulation-only, demonstrated=false (not claimed here).

---

## Sources
- Liu et al., *Nature* 559:593 (2018) — https://www.nature.com/articles/s41586-018-0332-7
- Nguyen, Heuer-Jungemann et al., *Angew. Chem. Int. Ed.* 58:912 (2019) — https://onlinelibrary.wiley.com/doi/abs/10.1002/anie.201811323
- Jing et al., *Nature Protocols* 14:2416 (2019) — https://www.nature.com/articles/s41596-019-0184-0
- Sun et al., *Science* 346:1258361 (2014) — https://www.science.org/doi/abs/10.1126/science.1258361
- Helmi et al., *Nano Lett.* 14:6693 (2014) — https://pubs.acs.org/doi/10.1021/nl503441v
- Shen, Keller et al., *Beilstein J. Nanotechnol.* 8:2503 (2017) — https://www.beilstein-journals.org/bjnano/articles/8/236
- Area-selective ALD on DNA, *ACS Nano* 14 (2020) — https://pubs.acs.org/doi/abs/10.1021/acsnano.0c04493
- ALD on DNA origami crystals, *JACS* 147 (2025) — https://pubs.acs.org/doi/10.1021/jacs.4c17232
- TEOS (LabPro) — https://labproinc.com/products/tetraethyl-orthosilicate-500ml-t0100-500ml
- APTES (Sigma 741442) — https://www.sigmaaldrich.com/US/en/product/aldrich/741442
- TMAPS (Gelest SIT8415.0) — https://www.gelest.com/product/SIT8415.0/
