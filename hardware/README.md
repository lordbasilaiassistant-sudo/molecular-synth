# /hardware — the desktop rig

Three subsystems, all from repurposed / online parts (full linked prices in
[`../bom/bom.md`](../bom/bom.md)). Rig hardware total ≈ **$623**, well under the
$1500 ceiling.

```
cad/        parametric OpenSCAD parts (edit the variables block, render to STL)
firmware/   Arduino thermocycler firmware + the host ramp streamer
```

## 1. Folding thermocycler (the one custom build) — ~$108

A Peltier/PID temperature box that runs the anneal ramp the compiler emits. DNA
origami folds in a single anneal (heat → slow-cool in Mg²⁺ buffer); a qPCR machine is
**not** required (many designs even fold isothermally — Sobczak 2012).

**Stack (bottom → top):** CPU heatsink + fan → **TEC1-12706 Peltier** → drilled
**aluminium block** holding 0.2 mL PCR tubes → printed insulating collar
(`cad/thermocycler_block.scad`) that clamps the stack and holds the thermistor.

**Wiring:**
```
12V 30A PSU ─┬─► BTS7960 H-bridge ─► Peltier (+/- reversible: heat & cool)
             └─► CPU fan (always on)
Arduino Uno: D9 → H-bridge PWM (EN), D7/D8 → direction (heat/cool),
             D5 → fan, A0 → 100k NTC thermistor (with 4.7k pull-up to 5V)
```

**Flash + run:**
```bash
# open firmware/thermocycler.ino in the Arduino IDE, select Uno, upload.
# then stream the compiled ramp (design.json -> STEP commands):
pip install pyserial
python firmware/host_ramp.py --design ../examples/out_cube/design.json --port COM3
python firmware/host_ramp.py --design ../examples/out_cube/design.json --dry-run  # no hardware
```
The firmware also runs a built-in 90→20 °C ramp on boot if no host is connected, with
a hard 99 °C cutoff. **Path A alternative:** float the PCR tubes in a sous-vide bath
and step the setpoint — zero electronics, good for first validation.

## 2. Fold verification — DIY gel (~$290 with imaging) + optional STM

**Agarose gel electrophoresis** is the real QC: a folded origami runs as one tight
band, distinct from excess staples (fast front) and aggregates (smear/well).
- Print `cad/gel_box.scad` (buffer tank + casting tray + comb), add stainless/Pt wire
  electrodes — **or** use the all-in-one IVYX system (its integrated 50/100 V supply
  meets the 60–90 V origami requirement; a 0–30 V bench supply will **not** work).
- Run **~2% agarose in 1× TAE + ~11 mM MgCl₂** (Mg in the gel *and* running buffer, or
  origami unfolds), **60–90 V, cold (on ice)**, stain with GelGreen, image on the
  470 nm blue transilluminator. Always run a scaffold-only lane + a ladder.

**Optional DIY STM (`cad/stm_mount.scad`) — atomic-resolution demonstrator (~$36 hw).**
A cut piezo-buzzer scanner + hand-cut Pt/Ir tip + LF356 transimpedance amp + Teensy
resolves the **atomic lattice of HOPG graphite** (Ma, HardwareX 2023; Berard).
**Honest framing:** it images graphite atoms, **not** the soft DNA origami — it's the
"atomic resolution is cheap & real" trophy, decoupled from product QC.

## 3. Hardening station (optional) — bench tools you already have on the list

Sol–gel silicification (DNA → rigid SiO₂; Liu 2018) needs only a **vortex mixer**
(~$35) + **mini centrifuge** (~$100) + ventilation + the silane reagents — no new
big-ticket hardware. ALD oxide coating is demonstrated but needs a vacuum reactor
(~$30k+) → route to an external nanofab service, not the desktop BOM.

## Rendering the CAD

Install the free [OpenSCAD](https://openscad.org). Each file has a parameters block at
the top and a `part = "..."` selector:
```bash
openscad -D 'part="buffer"' -o buffer.stl cad/gel_box.scad
openscad -D 'part="collar"' -o collar.stl cad/thermocycler_block.scad
openscad -D 'part="base"'   -o base.stl   cad/stm_mount.scad
```
