# Bill of Materials — Molecular Synth v0

_Auto-generated from [`bom.json`](bom.json) by `render_bom.py` (the same file the
[validation gate](../validate/validate.py) checks). Prices are snapshot estimates
(USA, 2026-06); treat as ±20% and verify at order time._

## Totals
- **Rig hardware: $623**  (target < $1500 — PASS)
- **Core consumables (per design): $570**  (staple oPool path; addressable plate adds ~$550)
- Optional tracks (STM, silica hardening, sous-vide) are listed separately and not in the rig total.

## Rig hardware (durable, the < $1500 rig)
| Part | Role | Repurposed from | Vendor | Price | Link |
|---|---|---|---|---|---|
| TEC1-12706 Peltier module (40x40 mm, 12 V, 60 W) | active heat AND cool element under the aluminium folding block | CPU cooler / dehumidifier thermoelectric module | Amazon (SMAKN) | $11 | [link](https://www.amazon.com/SMAKNTM-TEC1-12706-Thermoelectric-Cooler-Peltier/dp/B00J3F7YKC) |
| BTS7960 IBT-2 H-bridge driver | bidirectional Peltier drive (PWM heat + reverse-polarity cool) for thermocycler.ino | smart-car / robot DC-motor driver module | Amazon (HiLetgo) | $12 | [link](https://www.amazon.com/HiLetgo-BTS7960-Driver-Arduino-Current/dp/B00WSN98DC) |
| Arduino Uno R3 | runs the anneal ramp, PID loop, drives the H-bridge, reads thermistor | hobby microcontroller | Arduino | $27 | [link](https://store.arduino.cc/products/arduino-uno-rev3) |
| 100K NTC 3950 thermistor (10-pack) | temperature feedback for the PID loop | 3D-printer hot-end / hot-bed sensor | Amazon (Cylewet) | $8 | [link](https://www.amazon.com/Cylewet-Thermistor-Temperture-Printer-CYT1064/dp/B06XR1TG5N) |
| 96-well aluminium PCR cooling block (0.2 mL) | even thermal mass holding the folding tubes on the Peltier | PCR/lab cooling block (consumer-sold) | Amazon | $15 | [link](https://www.amazon.com/Aluminum-Cooling-Block-%EF%BC%8C96-Well-96-Well/dp/B09MJHY27W) |
| 12 V 30 A 360 W switching PSU | powers the Peltier + electronics | LED-strip / 3D-printer power supply | Amazon (EAGWELL) | $25 | [link](https://www.amazon.com/EAGWELL-Universal-Regulated-Switching-Computer/dp/B06XW76584) |
| CPU heatsink + 12 V fan | dumps the Peltier hot-side heat | PC CPU cooler | Amazon | $10 | [link](https://www.amazon.com/s?k=cpu+heatsink+12v+fan) |
| IVYX Scientific Mini Gel Electrophoresis System (tank + integrated 35/50/100 V supply + combs) | fold-QC gel; the integrated 50/100 V supply meets the 60-90 V origami requirement | education-grade all-in-one gel rig | Amazon (IVYX) | $160 | [link](https://www.amazon.com/Electrophoresis-System-Power-Supply-Timer/dp/B0B2ZSRG2Z) |
| Blue-LED transilluminator (470 nm) | visualize GelGreen/GelRed-stained bands (eye/skin-safe, no UV) | blue-light gel imager | Amazon | $130 | [link](https://www.amazon.com/Light-Transilluminator-470nm-Electrophoresis-Visualization/dp/B0B2ZDFM8D) |
| Mini vortex mixer | mix folding + silicification reactions | nail-polish / paint / tattoo-ink vortex (same device) | Amazon (INTLLAB) | $35 | [link](https://www.amazon.com/INTLLAB-Function-Adhesives-Vortexer-Stainless/dp/B0CWL3TP83) |
| Mini benchtop centrifuge (7000 rpm) | spin-downs + PEG-precipitation purification of folded origami | lab/hobby microcentrifuge | Amazon (CryoKing) | $100 | [link](https://www.amazon.com/CryoKing-Centrifuges-Centrifuge-Microcentrifuge-Laboratory/dp/B0DHXHKGK7) |
| Adjustable micropipette set (2-20, 20-200, 100-1000 uL) + tips | dispense uL volumes for all wet steps | lab micropipettes (sold direct to consumers) | Amazon | $90 | [link](https://www.amazon.com/s?k=adjustable+micropipette+set+2-1000ul) |

## Consumables (per design / reusable starter kit)
| Part | Role | Repurposed from | Vendor | Price | Link |
|---|---|---|---|---|---|
| M13mp18 single-stranded scaffold DNA (NEB N4040, 10 ug) | the scaffold strand the compiler threads (p7249, 7249 nt) | purpose-made consumable (sequencing/cloning template) | NEB | $40 | [link](https://www.neb.com/products/n4040-m13mp18-single-stranded-dna) |
| Staple oligos as IDT oPool (~200 sequences, one tube) | the staple set; cheapest route for a first proof-of-fold | purpose-made consumable | IDT | $200 | [link](https://www.idtdna.com/pages/products/custom-dna-rna/dna-oligos/custom-dna-oligos/opools-oligo-pools) |
| MgCl2 hexahydrate, ACS, 500 g | folding cation (12.5 mM Mg2+) + gel running buffer (~11 mM) | ACS reagent (consumer-sold) | Amazon (GFS) | $35 | [link](https://www.amazon.com/GFS-Chemicals-48801-Magnesium-Hexahydrate/dp/B01NBML9XZ) |
| 50x TAE buffer concentrate, 1 L | folding + gel buffer (dilute to 1x) | purpose-made consumable | Amazon | $25 | [link](https://www.amazon.com/50X-TAE-Buffer-Tris-Acetate-EDTA-1L/dp/B09V5MVMN9) |
| Agarose, molecular-biology grade, 100 g | gel matrix (~2% for origami QC) | purpose-made consumable | Amazon | $45 | [link](https://www.amazon.com/Agarose-Molecular-Biology-Grade-P05-SR01-100/dp/B00S9ZJFLI) |
| GelGreen nucleic-acid stain, 10000x, 0.5 mL | DNA-safe band stain (EtBr replacement; blue-light optimized) | purpose-made consumable | Amazon (Biotium) | $110 | [link](https://www.amazon.com/GelGreen-Nucleic-Acid-Stain-Water/dp/B07RY6BJMT) |
| DNA ladder (100 bp - 1 kb) | size marker lane on the gel | purpose-made consumable | Amazon (IVYX) | $40 | [link](https://www.amazon.com/IVYX-Scientific-Ladders-Electrophoresis-100bp/dp/B0GPMJCW2Q) |
| PEG-8000, 500 g | PEG-precipitation purification of folded origami (Stahl 2014) | consumer-sold reagent | Amazon | $40 | [link](https://www.amazon.com/s?k=peg+8000+500g) |
| 0.2 mL PCR 8-tube strips (~125) | folding-reaction vessels | purpose-made consumable | Amazon | $15 | [link](https://www.amazon.com/PCR-Tubes-0-2ml-Strip-Included/dp/B09CVDBMQ9) |
| Nuclease-free water, 1 L | all dilutions / buffers | purpose-made consumable | Amazon | $20 | [link](https://www.amazon.com/Quality-Biological-351-029-131-Molecular-Endotoxin/dp/B07T14KWBZ) |

## Optional (alternative + stretch-track parts)
| Part | Role | Repurposed from | Vendor | Price | Link |
|---|---|---|---|---|---|
| Sous-vide immersion circulator (alternative folding bath) | isothermal / manual-step folding (Sobczak 2012); zero-electronics Path A | kitchen sous-vide cooker | Amazon | $60 | [link](https://www.amazon.com/s?k=sous+vide+immersion+circulator) |
| 3D-printed gel box + thermocycler collar + STM mount (PLA/PETG filament) | the parametric hardware/cad/*.scad parts | 3D printer filament | Amazon | $15 | [link](https://www.amazon.com/s?k=petg+filament+1kg) |
| Piezo buzzer disc 27 mm (15-pack) [STM] | cut into quadrants -> XYZ scanner (Berard/Open-STM) | doorbell / alarm piezo buzzer | Amazon | $9 | [link](https://www.amazon.com/15-Pieces-Elements-Electrode-Oscillator/dp/B00DH2UKYO) |
| Teensy 4.0 [STM] | real-time STM scan/feedback controller | hobby microcontroller | Adafruit | $25 | [link](https://www.adafruit.com/product/4323) |
| LF356 JFET op-amp [STM] | transimpedance amp: pA-nA tunnelling current -> voltage | general-purpose op-amp | Mouser | $2 | [link](https://www.mouser.com/c/?series=LF356) |
| TEOS (tetraethyl orthosilicate), 500 mL [hardening] | silica source for sol-gel hardening (Liu 2018) | consumer-sold reagent | LabPro | $42 | [link](https://labproinc.com/products/tetraethyl-orthosilicate-500ml-t0100-500ml) |
| APTES or TMAPS aminosilane (nucleator) [hardening] | cationic/amine nucleation layer on DNA before silica condensation | consumer/lab reagent | Sigma-Aldrich | $178 | [link](https://www.sigmaaldrich.com/US/en/product/aldrich/741442) |
| Pt/Ir wire 90:10, 0.25 mm, 30 cm [STM] | hand-cut STM tip (~50 tips per length) | consumer-sold precious-metal wire | Surepure Chemetals | $60 | [link](https://www.surepure.com/Platinum-Iridium-Wire-Rod-90-Percent-Platinum-10-Percent-Iridium/a/1432,1,815) |
| HOPG sample (grade B, 5x5x1 mm) [STM] | conductive test specimen whose atomic lattice the STM resolves | consumer-sold graphite sample | Amazon | $90 | [link](https://www.amazon.com/Oriented-Pyrolytic-Graphite-Priority-Shipping/dp/B08D94B6JW) |

---
_Honesty notes: search-URL lines (CPU cooler, filament, PEG, pipette set, sous-vide)
point at a live orderable category rather than one SKU — pick any reputable listing.
The compiler emits both an oPool order (`staples_opool.txt`, ~$200) and an addressable
plate order (`staples_idt_plate.txt`, ~$750); choose your cost point._
