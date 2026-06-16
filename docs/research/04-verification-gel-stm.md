# Domain 04 — Verification: Did the product fold? What does it look like?

**Project:** Molecular Synth v0 — desktop DNA-origami nanofabrication rig + shape→staple compiler.
**This domain:** *Quality control / verification* of the assembled product. Two independent tracks:

1. **DIY agarose gel electrophoresis** — the workhorse, honest QC tool. A correctly folded origami runs as a tight, fast band distinct from leftover staples (small, runs ahead) and aggregates/misfolds (large/smeared, runs behind or stuck in the well). This is real, in-budget, and is exactly how origami labs do first-pass QC.
2. **DIY scanning tunneling microscope (STM)** — an *atomic-resolution capability demonstrator*. A hobby STM (Dan Berard / Open-STM design) reliably resolves the atomic lattice of HOPG (graphite) in air. **It does NOT image a soft DNA origami in solution.** It is included as proof that atomic-scale imaging is achievable on a hobby budget — a north-star instrument — NOT as the origami QC tool. Be honest about this everywhere.

---

## TRACK 1 — Agarose gel electrophoresis (the real QC method)

### Why this is the right tool
Agarose gel electrophoresis separates DNA by size/conformation under an electric field. For scaffolded DNA origami:
- **Well-folded monomer** → compact, high mobility → one tight leading band.
- **Excess staple strands** (the 200+ short oligos added in excess) → tiny, run far ahead as a diffuse front.
- **Aggregates / misfolds / multimers** → larger/slower, smear, or stick in the loading well.

Comparing the folded-sample lane against the raw scaffold lane (e.g. M13mp18, ~7,249 nt) tells you at a glance whether folding worked. This is standard practice and is documented in the canonical origami protocols below.

### Scientific citations (all verified via web search)

1. **Rothemund, P. W. K.** "Folding DNA to create nanoscale shapes and patterns." *Nature* 440, 297–302 (2006). DOI: 10.1038/nature04586. https://www.nature.com/articles/nature04586
   - The origin of scaffolded DNA origami. **Demonstrated = true** (AFM images of folded shapes ~100 nm). Establishes the whole product category. Scope: 2D shapes ~100 nm, AFM-verified.

2. **Castro, C. E.; Kilchherr, F.; Kim, D.-N.; Shiao, E. L.; Wauer, T.; Wortmann, P.; Bathe, M.; Dietz, H.** "A primer to scaffolded DNA origami." *Nature Methods* 8, 221–229 (2011). DOI: 10.1038/nmeth.1570. https://www.nature.com/articles/nmeth.1570
   - The practical "how-to" reference. **Its Supplementary Protocol 3 is literally "Agarose Gel Electrophoresis (EtBr) with DNA origami objects."** This is the citation that grounds gel-based origami QC. **Demonstrated = true** (gels + TEM of 3D objects). Scope: describes gel conditions (≈2% agarose, ~11 mM MgCl₂ in running buffer, ~70 V, ice-cooled) and folding-quality readout.

3. **Stahl, E.; Martin, T. G.; Praetorius, F.; Dietz, H.** "Facile and Scalable Preparation of Pure and Dense DNA Origami Solutions." *Angew. Chem. Int. Ed.* 53(47), 12735–12740 (2014). DOI: 10.1002/anie.201405991. https://onlinelibrary.wiley.com/doi/10.1002/anie.201405991 (open access PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4253120/)
   - Purification of folded origami. The headline method is **PEG (poly-ethylene-glycol) precipitation**, but the paper benchmarks purity against **gel-based purification/QC** and is the standard citation for getting pure, dense origami after folding. **Demonstrated = true.** Scope note: PEG precipitation is the *scalable* purification; gel excision is the classic small-scale purification. Both rely on the gel as the readout of what's folded.

### Honest scope of Track 1
- A gel tells you **folded vs. not-folded and roughly monodisperse vs. aggregated**. It does **NOT** tell you the *shape* or give nm-resolution images. Shape confirmation needs AFM/TEM (out of hobby budget). The gel is necessary-but-not-sufficient first-pass QC — and it's the single most valuable cheap instrument in the whole rig.
- Origami gels are run **cold** (on ice / in a fridge) and need **Mg²⁺ in the running buffer** (origami falls apart without ~10 mM Mg²⁺). Plain TAE alone is for the scaffold control; origami lanes need TAE + ~11 mM MgCl₂. This is a real gotcha the compiler/protocol docs must surface.

### Voltage note (load-bearing)
Origami gels run at **~60–90 V** for 1.5–3 h, cold. A standard adjustable **0–30 V** bench supply is therefore **NOT sufficient** for the gel. Options, in order of preference:
- Use the **gel kit's own integrated power supply** (the IVYX mini system supplies 35/50/100 V presets — 50 V or 100 V both usable).
- Or a dedicated electrophoresis power supply.
- Or a boost-converter / stacked-battery rig (DIY, riskier).
Do **not** spec a 0–30 V bench unit as the gel driver — it will not push origami through 2% agarose in reasonable time.

### Parts — Track 1 (gel)

| Part | Role | Vendor | ~Price | Category | Notes |
|---|---|---|---|---|---|
| IVYX Scientific Mini Gel Electrophoresis System (tank + integrated 35/50/100 V supply + 2 casting sets + combs) | Complete gel rig incl. power supply at origami-compatible 50–100 V | Amazon (IVYX) | ~$160 | rig-hardware | All-in-one; the integrated supply solves the 60–90 V requirement. https://www.amazon.com/Electrophoresis-System-Power-Supply-Timer/dp/B0B2ZSRG2Z |
| Frey Scientific Single-Gel Apparatus (platinum electrodes, acrylic tank, 12-well combs) — *alternative tank* | Acrylic casting/run tank with Pt electrodes (needs external supply) | Amazon | ~$70 | optional | Pt electrodes, but power supply NOT included; pair with the IVYX or a 100 V supply. https://www.amazon.com/Frey-Scientific-1267918-Single-Gel-Electrophoresis/dp/B008C4PAKG |
| Blue LED Transilluminator, 470 nm | Visualize GelRed/GelGreen/SYBR-stained bands (blue light = eye/skin safe, no UV) | Amazon | ~$130 | rig-hardware | Blue-light is the hobbyist-safe choice; pairs with green dyes. https://www.amazon.com/Light-Transilluminator-470nm-Electrophoresis-Visualization/dp/B0B2ZDFM8D |
| GelGreen Nucleic Acid Gel Stain, 10,000X, 0.5 mL (Biotium) | DNA-safe fluorescent stain (replaces ethidium bromide; non-mutagenic, drain-disposable) | Amazon (Biotium) | ~$110 | consumable | Optimized for blue-light transilluminator. https://www.amazon.com/GelGreen-Nucleic-Acid-Stain-Water/dp/B07RY6BJMT |
| 50X TAE Buffer concentrate, 1 L | Running/gel buffer (dilute to 1X; add MgCl₂ for origami lanes) | Amazon | ~$25 | consumable | https://www.amazon.com/50X-TAE-Buffer-Tris-Acetate-EDTA-1L/dp/B09V5MVMN9 |
| Agarose, Molecular Biology Grade, 100 g | Gel matrix (run ~2% for origami) | Amazon | ~$45 | consumable | https://www.amazon.com/Agarose-Molecular-Biology-Grade-P05-SR01-100/dp/B00S9ZJFLI |
| DNA Ladder (100 bp – 1 kb) | Size marker lane | Amazon (IVYX) | ~$40 | consumable | https://www.amazon.com/IVYX-Scientific-Ladders-Electrophoresis-100bp/dp/B0GPMJCW2Q |

*MgCl₂ (for ~11 mM in origami running buffer) is a cheap commodity reagent and should be added to the consumables list separately.*

---

## TRACK 2 — DIY STM (atomic-resolution capability demonstrator)

### What it is and is NOT
- **IS:** A working scanning tunneling microscope built from a cut piezo buzzer (quadrant scanner), a hand-cut Pt/Ir (or W) tip, a transimpedance amplifier (current-to-voltage), an Arduino/Teensy controller, and vibration isolation. On **conductive HOPG (graphite)** in air it resolves the **atomic lattice** — individual carbon atom positions.
- **IS NOT:** A tool that images DNA origami. Origami is soft, insulating, ~10–100 nm tall, and sits in aqueous Mg²⁺ buffer. A hobby air-STM cannot image it. (Lab origami imaging uses AFM in liquid or cryo-TEM — out of budget.) **Frame the STM honestly as the "we can resolve single atoms on a desktop" demonstrator / north-star instrument, not the QC path for the product.**

### Scientific / design citations (all verified)

4. **Berard, D.** Open-source "Scanning Tunneling Microscope" (Hackaday.io project #4986, 2015). https://hackaday.io/project/4986-scanning-tunneling-microscope
   - The canonical hobby STM. Uses a **piezo buzzer cut into quadrants** as the scanner, a **tip cut from tungsten/Pt-Ir wire**, sapphire tip mount, fine Z screws. **Demonstrated = true** — Berard imaged **HOPG with atomic resolution in air**. Scope: images the graphite lattice; does NOT image soft/biological samples. (Project page is not peer-reviewed, but the result is reproduced in the peer-reviewed Open-STM paper below.)

5. **Ma, W. (Institute of Optics and Electronics, Chinese Academy of Sciences).** "Open STM: A low-cost scanning tunneling microscope with a fast approach method." *HardwareX* 17, e00504 (2023). DOI: 10.1016/j.ohx.2023.e00504. https://www.hardware-x.com/article/S2468-0672(23)00111-6/fulltext (open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC10825635/)
   - **Peer-reviewed** open-hardware STM, total cost **~$300 / 2000 CNY**, control voltage ≤15 V, 45×45×31.5 mm. **Demonstrated = true** — imaged **HOPG and resolved atomic features** at 50–60 mV bias. This is the citation that makes "hobby STM resolves the atomic lattice" a peer-reviewed claim, not just a hobbyist blog. Scope: HOPG / conductive flat samples only; not biological, not in liquid.

### Honest scope of Track 2
- **demonstrated = true** for "resolves HOPG atomic lattice on a ~$300 desktop build."
- **demonstrated = false / N-A** for any claim that the STM images the DNA origami product. State plainly: the STM and the origami never touch the same sample. It is the "atomic-resolution is real and cheap" trophy, decoupled from product QC.

### Parts — Track 2 (STM)

| Part | Role | Vendor | ~Price | Category | Notes |
|---|---|---|---|---|---|
| Piezo buzzer disc, 27 mm (multi-pack) | Cut into quadrants → XYZ scanner (the Berard trick) | Amazon | ~$9 (15-pack) | rig-hardware | Repurposed from doorbell/alarm buzzers. https://www.amazon.com/15-Pieces-Elements-Electrode-Oscillator/dp/B00DH2UKYO |
| Platinum/Iridium wire, 0.25 mm, 90:10 Pt:Ir, ~30 cm | Hand-cut STM tip (1 length → ~50 tips) | Surepure Chemetals / Nanosurf | ~$60 | consumable | https://www.surepure.com/Platinum-Iridium-Wire-Rod-90-Percent-Platinum-10-Percent-Iridium/a/1432,1,815 (or Nanosurf https://shop.nanosurf.com/products/accessories/pt-ir-wire,-0-25mm-30cm) |
| HOPG sample (Grade B, 5×5×1 mm) | The conductive test specimen whose atomic lattice the STM resolves | Amazon | ~$90 | consumable | https://www.amazon.com/Oriented-Pyrolytic-Graphite-Priority-Shipping/dp/B08D94B6JW (cheaper grade B is fine for atomic imaging; ZYH lab grade from MSE Supplies is the upgrade) |
| Teensy 4.0 microcontroller | Real-time scan control / DAC-ADC loop | Adafruit / SparkFun / PJRC | ~$25 | rig-hardware | https://www.adafruit.com/product/4323 |
| LF356 JFET-input op-amp (DIP-8) | Transimpedance amplifier — converts pA–nA tunneling current to voltage | Mouser / DigiKey / Amplified Parts | ~$2 | rig-hardware | JFET input = low bias current, needed for tunneling currents. https://www.mouser.com/c/?series=LF356 (datasheet TI: https://www.ti.com/product/LF356). OPA129/OPA111 are higher-end upgrades. |

**Additional STM consumables (commodity, list separately):** high-value feedback resistor (~100 MΩ for the TIA), sapphire/ceramic tip mount, fine-pitch Z adjustment screws, and a vibration-isolation stack (bungee + stacked steel plates + Sorbothane — all repurposed hardware, well under $50).

---

## Budget roll-up (rig hardware only; target < $1500)

| Track | Rig-hardware items | Subtotal |
|---|---|---|
| Gel | IVYX gel system ($160) + blue transilluminator ($130) | ~$290 |
| STM | piezo buzzer ($9) + Teensy ($25) + LF356 ($2) | ~$36 |
| **Total rig hardware** | | **~$326** |

Consumables (counted separately): GelGreen (~$110), TAE (~$25), agarose (~$45), DNA ladder (~$40), Pt/Ir wire (~$60), HOPG (~$90), MgCl₂ + TIA resistor + tip mount + isolation (~$50). Consumables ≈ **$420**.

Both tracks together come in **far under the $1500 rig budget** — the verification domain is the cheapest part of the whole Molecular Synth v0.

---

## Compiler / software facts (for the shape→staple toolchain to surface)
- **Gel readout logic:** folded origami = tight leading band; staples = fast diffuse front; aggregate/misfold = smear or well-stuck slow band. Always run a **scaffold-only control lane** (M13mp18, ~7,249 nt) and a **ladder lane** for comparison.
- **Origami gel running buffer needs Mg²⁺** (~11 mM MgCl₂ in 1× TAE); without it origami unfolds. Plain 1× TAE only for the scaffold control. The compiler's protocol export must emit this buffer recipe.
- **Gel conditions:** ~2% agarose, ~60–90 V, **run cold (on ice / in fridge)**, GelGreen stain, blue-light (470 nm) visualization. Run 1.5–3 h.
- **STM controller:** Teensy 4.0 firmware (Arduino IDE / Teensyduino), real-time PID feedback holding constant tunneling current; bias ~50–60 mV for HOPG; control voltages ≤15 V (per Open-STM). Transimpedance amp = LF356 with ~100 MΩ feedback. Image data is an XY raster of Z-height → render as PNG/heightmap.
- **Honest separation in software/UX:** the STM module is a separate "atomic-imaging demo" feature; the **gel module is the product-QC feature.** Do not let the UI imply the STM verifies the origami.
