# 02 — The Folding Reaction + Repurposed Thermocycler Hardware

**Domain:** Molecular Synth v0 — the thermal annealing step that drives scaffolded DNA origami
self-assembly, and the cheapest honest hardware that can run it.

**One-line truth:** DNA origami folding is a *single-pot anneal*: mix one long "scaffold" strand +
~200 short "staple" strands in a Mg²⁺ buffer, heat to denature, then cool slowly. The "machine" is
nothing more than a programmable temperature box. A real qPCR thermocycler is **not required** — a
PID-controlled heat block, a sous-vide circulator, or even an isothermal hold can fold many designs.
This is the most de-risked subsystem of the whole rig.

---

## 1. The canonical folding protocol (web-verified)

### 1.1 Rothemund 2006 — the founding paper

Paul W. K. Rothemund, *"Folding DNA to create nanoscale shapes and patterns,"* **Nature 440,
297–302 (2006)**, DOI: 10.1038/nature04586.
<https://www.nature.com/articles/nature04586>

- Mechanism: a ~7-kilobase single-stranded **scaffold** (M13mp18 phage genome, ~7249 nt) is
  "raster-filled" through the target 2D shape; ~200+ short synthetic **staple strands**
  (each ~32 nt) cross-link the scaffold back on itself at crossovers.
- Self-assembly is **a single step**: mix, heat, cool. Staples pull the scaffold into shape as the
  solution cools.
- Result: ~100 nm structures (squares, disks, triangles, a 5-pointed star, a smiley face) at ~6 nm
  spatial resolution. **This bounds the whole product: origami makes ~10 nm–1 µm objects, not
  macroscopic ones.**
- Rothemund's original anneal: heat to ~90–95 °C, cool to ~20 °C at ~1 °C/min over ~2 hours, in
  TAE buffer + ~12.5 mM MgCl₂, staples in large excess over scaffold.

### 1.2 Castro et al. 2011 — the practical primer (THE protocol reference)

Castro C. E., Kilchherr F., Kim D.-N., Shiao E. L., Wauer T., Wortmann P., Bathe M., Dietz H.,
*"A primer to scaffolded DNA origami,"* **Nature Methods 8, 221–229 (2011)**,
DOI: 10.1038/nmeth.1570. <https://www.nature.com/articles/nmeth.1570>

- The step-by-step community standard for designing (caDNAno), folding, purifying, and imaging
  origami. Introduces CanDo for predicting 3D solution shape + flexibility.
- Folding mix: scaffold + staples in **1× TAE buffer with added MgCl₂** (commonly 12.5–20 mM Mg²⁺
  depending on 2D vs 3D), staples at **~5–10× molar excess** per scaffold.
- Thermal annealing ramp from denaturation (~65–80 °C) down to RT; complex 3D objects often need a
  long, slow ramp (hours to days) and a **per-design MgCl₂ + temperature screen**.

### 1.3 Wagenbauer et al. 2017 — modern "How We Make DNA Origami"

Wagenbauer K. F., Engelhardt F. A. S., Stahl E., Hechtl V. K., Stömmer P., Seebacher F.,
Meregalli L., Ketterer P., Gerling T., Dietz H., *"How We Make DNA Origami,"*
**ChemBioChem 18(19), 1873–1885 (2017)**, DOI: 10.1002/cbic.201700377.
<https://chemistry-europe.onlinelibrary.wiley.com/doi/abs/10.1002/cbic.201700377>

- The current bench-reality protocol from the Dietz lab. Confirms folding is dominated by two
  knobs you screen empirically: **MgCl₂ concentration** and **thermal ramp**.
- Standard reaction: ~20 nM scaffold + ~100–200 nM each staple (so ~5–10× per staple) in TAE-Mg²⁺.

### 1.4 Consensus reaction recipe (what the compiler should emit)

| Parameter | Value | Source |
|---|---|---|
| Scaffold | M13mp18-derived ssDNA (p7249 / p7560 / p8064), 10–20 nM | Rothemund 2006; Wagenbauer 2017 |
| Staples | ~5–10× molar excess per staple (e.g. 100 nM each at 20 nM scaffold) | Castro 2011; Wagenbauer 2017 |
| Buffer | 1× TAE (40 mM Tris-acetate, 1 mM EDTA) | Castro 2011 |
| MgCl₂ | **12.5 mM** default (2D); 16–20 mM for dense 3D; 5–10 mM for wireframe | Castro 2011; Wagenbauer 2017 |
| Denature | 90–95 °C hold ~5 min (2D) or 65–80 °C (gentle 3D) | Rothemund 2006; Castro 2011 |
| Anneal | slow cool to 20–25 °C | all |
| Total time | ~2 h (simple 2D) to 12–60 h (complex 3D) | Rothemund 2006; Castro 2011 |

---

## 2. Do you actually need a thermocycler? (No — strong evidence)

This is the budget-critical question. Three independent literature results say a precise programmable
ramp is sufficient and that **isothermal folding is even possible**, so a $35 PID heat block or a
sous-vide circulator replaces a $3k–10k qPCR machine.

### 2.1 Slow linear/controlled cool is the workhorse

- Rothemund's own 2D shapes folded on a simple cool from ~90 °C → 20 °C at ~1 °C/min (~2 h). A
  heat block or water bath with a slow controlled ramp reproduces this.
- Community protocols (e.g. the open iNANO/Dresden origami protocol) use ramps like 65 °C → 25 °C
  over hours, or nonlinear 16 h ramps — all of which a microcontroller-driven heater can execute.
  <https://inanobotdresden.github.io/origami-protocol.html>

### 2.2 Isothermal folding — no ramp at all (Dietz lab)

Sobczak J.-P. J., Martin T. G., Gerling T., Dietz H., *"Rapid folding of DNA into nanoscale shapes
at constant temperature,"* **Science 338, 1458–1461 (2012)**, DOI: 10.1126/science.1229919.
<https://www.science.org/doi/10.1126/science.1229919>

- Demonstrated that many origami objects fold to high yield by simply **holding at a single
  constant temperature** (each design has an optimal folding temperature, often ~45–60 °C), some
  in **minutes**. This means a fixed-setpoint heater/water bath can fold real structures — no ramp
  hardware needed for those designs.

### 2.3 Isothermal with denaturant / in cell media (even gentler hardware)

- Jiang, Z. et al. (representative) and follow-on work show isothermal assembly using denaturing
  agents (formamide) at lower temperatures, and ultra-fast isothermal formation of DNA
  nanostructures in culture media — further loosening the temperature-control requirement.
  *Isothermal Assembly of DNA Origami Structures Using Denaturing Agents*, **J. Am. Chem. Soc.**
  <https://pubs.acs.org/doi/10.1021/ja8030196>

**Honest scope caveat:** isothermal/slow-cool works *well for robust designs* (2D sheets, simple
bundles). **Dense 3D origami** (Dietz-style honeycomb/square-lattice solids) still folds best with a
multi-hour optimized ramp and a per-design MgCl₂ × temperature screen — exactly what a *programmable*
PID box (not just a fixed bath) buys you. So: build the programmable PID heat block, and you get both
the easy isothermal cases and the harder ramp cases.

---

## 3. The repurposed hardware (orderable today, USA, no lab account)

Design: a small **aluminum heat block** holding 0.2 mL PCR tubes, sandwiched on a **Peltier (TEC)**
for active heat *and* cool, the TEC's hot side bonded to a **CPU heatsink+fan**, driven by a
**power MOSFET** from a **12 V PSU**, with a **PID controller / Arduino + thermistor** closing the
loop. This is just a 3D-printer-hotend / PC-cooling / sous-vide stack rebadged as a thermocycler.

### Path A — fastest, dumbest, cheapest: sous-vide immersion circulator
A consumer sous-vide circulator already *is* a ±0.1 °C closed-loop water bath. Float PCR tubes in
the bath, set the isothermal folding temp (Sobczak 2012) or step it manually for a coarse ramp.
~$50–80, zero electronics. Best first validation.

### Path B — programmable ramp box (the real rig): PID + Peltier
| Part | Role | Repurposed from | Vendor | ~Price |
|---|---|---|---|---|
| TEC1-12706 Peltier (40×40 mm, 12 V, 60 W) | active heat + cool element under the block | CPU/cooler/dehumidifier TEC | Amazon (SMAKN/DAOKI etc.) | $8–13 |
| Inkbird ITC-100VH PID + SSR + K-probe kit | closed-loop temperature control (no-code path) | brewing/sous-vide/kiln controller | Amazon / inkbird.com | $35 |
| Arduino Uno R3 (programmable-ramp path) | runs the ramp schedule, PWM the MOSFET, read thermistor | hobby microcontroller | store.arduino.cc | $27 (Uno R3 SMD) / ~$10 clones |
| IRLB8721 logic-level N-MOSFET | Arduino-driven power switch for the TEC | 3D-printer/Arduino power switching | Amazon (BOJACK 10-pk) | ~$8 / 10 |
| 100K NTC 3950 thermistor (3D-printer hotend type) | temperature feedback into Arduino | 3D-printer hotbed/hotend sensor | Amazon (Cylewet/Gikfun 10-pk) | ~$8 / 10 |
| 96-well aluminum PCR cooling block (0.2 mL) | holds tubes, even thermal mass on the TEC | lab/PCR cooling block (consumer-sold) | Amazon | ~$15 |
| 12 V 30 A 360 W switching PSU (w/ fan) | powers TEC + electronics | LED-strip / 3D-printer PSU | Amazon (EAGWELL/ALITOVE) | ~$25 |
| CPU heatsink + 12 V fan (≥40 mm) | dumps TEC hot-side heat | PC CPU cooler | Amazon | ~$10 |

**Rig hardware subtotal (Path B): ~$135–150.** Well under the $1500 ceiling — leaves headroom for a
USB microscope/imaging subsystem and an electrophoresis verification rig (covered in other docs).
Consumables (scaffold, staple oligo pool, TAE, MgCl₂, PCR tubes) are counted separately.

### Why a TEC, not just a resistive heater
Folding needs both a fast **heat** to 90 °C and a **controlled cool**. A bare resistive cartridge
can only heat; cooling then relies on ambient loss (slow, uncontrolled). A Peltier reverses polarity
to actively pump heat out, giving a *controlled* downward ramp — the variable that matters most for
yield. (For Path A, the circulator's pump + ambient handles cooling.)

---

## 4. code_facts — exact numbers the compiler must emit

The software compiler ("shape → staple recipe") should output a folding protocol block with these
defaults, overridable per design class:

- **Buffer:** `1x TAE` (40 mM Tris-acetate, 1 mM EDTA, pH ~8.3) `+ 12.5 mM MgCl2` (default 2D).
  - 3D dense lattice: bump MgCl₂ to `16-20 mM`. Wireframe: drop to `5-10 mM`.
- **Concentrations:** scaffold `20 nM`; each staple `100 nM` → **5× per staple** (use `200 nM` for
  10×). Equivalently emit "staple:scaffold = 5–10×".
- **Default slow-ramp schedule (2D, ~2 h):**
  - hold `95 °C` for `5 min` (denature)
  - linear cool `95 °C → 20 °C` at **`1 °C / min`** (≈75 min)
  - hold `20 °C` (store at 4 °C)
- **Standard 3D ramp (Dietz-style, overnight):**
  - hold `65 °C` for `15 min`
  - ramp `60 °C → 40 °C` at **`−1 °C / hour`** (the design-critical window), then fast cool to 20 °C
  - total ~20–60 h depending on object
- **Isothermal option (Sobczak 2012):** single hold at the design's optimal fold temp, typically in
  the `45–60 °C` band, for `minutes to hours`; emit as `ISOTHERMAL T=<screened>°C`.
- **MgCl₂ × temperature screen grid** the compiler should suggest when yield is unknown:
  MgCl₂ ∈ {5, 8, 12.5, 16, 20} mM × fold-temp/ramp-window ∈ {coarse ramp, hold 50, 55, 60 °C}.
- **Scaffold identity:** M13mp18-derived, length matched to design (`p7249`, `p7560`, or `p8064`).
- **Staple length:** ~`32 nt` typical (caDNAno crossover spacing); pool = "one tube per staple" or
  premixed equimolar pool.
- **Anneal volume:** 0.2 mL PCR tubes, ~50 µL reaction; ramp executed in the aluminum block on the
  TEC (PID setpoint stream) or in the sous-vide bath.
- **PID/Arduino control facts:** 100K NTC 3950 thermistor + matching pull-up (typ. 4.7 kΩ) on an
  ADC pin; Steinhart-Hart or β=3950 conversion; PWM the IRLB8721 gate to modulate TEC power;
  the ramp program is just a setpoint-vs-time table the firmware interpolates.

---

## 5. Honest scope / what this subsystem does NOT do

- It controls **temperature only**. It does not synthesize DNA, image the product, or verify yield —
  those are separate subsystems (oligo ordering is a consumable; AFM/gel/USB-scope is verification).
- Folding makes **~10 nm–1 µm** addressable nanostructures. It is **not** Drexler/diamondoid
  mechanosynthesis — that remains **simulation/theory only, demonstrated=false, north-star**. DNA
  origami is the real, demonstrated path to atomically-*defined* (sequence-addressed) nanoscale
  assembly, not atomically-precise covalent diamond machining.
- Yield is design-dependent. The hardware gives you the knobs (Mg²⁺, ramp); achieving high yield on
  a *new* shape still requires the empirical screen described above.

---

## Sources
- Rothemund 2006, Nature — <https://www.nature.com/articles/nature04586>
- Castro et al. 2011, Nature Methods — <https://www.nature.com/articles/nmeth.1570>
- Wagenbauer et al. 2017, ChemBioChem — <https://chemistry-europe.onlinelibrary.wiley.com/doi/abs/10.1002/cbic.201700377>
- Sobczak et al. 2012, Science — <https://www.science.org/doi/10.1126/science.1229919>
- Isothermal w/ denaturant, JACS — <https://pubs.acs.org/doi/10.1021/ja8030196>
- Open origami protocol (Dresden) — <https://inanobotdresden.github.io/origami-protocol.html>
- Parts: TEC1-12706 <https://www.amazon.com/SMAKNTM-TEC1-12706-Thermoelectric-Cooler-Peltier/dp/B00J3F7YKC> ·
  Inkbird ITC-100VH <https://www.amazon.com/Inkbird-Thermostat-Temperature-Controller-ITC-100VH/dp/B00T2IODEK> ·
  Arduino Uno R3 <https://store.arduino.cc/products/arduino-uno-rev3> ·
  IRLB8721 <https://www.amazon.com/BOJACK-IRLB8721-Transistors-IRLB8721PBF-N-Channel/dp/B083WMH7CD> ·
  NTC 3950 <https://www.amazon.com/Cylewet-Thermistor-Temperture-Printer-CYT1064/dp/B06XR1TG5N> ·
  Al PCR block <https://www.amazon.com/Aluminum-Cooling-Block-%EF%BC%8C96-Well-96-Well/dp/B09MJHY27W> ·
  12V 30A PSU <https://www.amazon.com/EAGWELL-Universal-Regulated-Switching-Computer/dp/B06XW76584>
