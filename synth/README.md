# /synth — Drink Synth (the buildable-today synthesizer)

"I want hot coffee." / "Iced oat latte, large, extra shot." → a request-compiler turns
it into a deterministic machine recipe → cheap hardware pours it. Same architecture as
the molecular compiler (request → compiler → machine recipe), at macroscale, for ~$120
of orderable parts. See [`../docs/vision.md`](../docs/vision.md) for why this is the
*real-today* rung of the synthesizer thesis (and what stays north-star).

> **Honest scope:** this **assembles a drink from stocked ingredients** with peristaltic
> pumps and a Peltier hot/cold plate. It does **not** synthesise matter from atoms.

## Try the compiler (no hardware, pure stdlib)

```bash
cd synth
python -m drinksynth make "iced oat latte, large, extra shot"
python -m drinksynth make "hot americano"
python -m drinksynth make "cold brew, sweet"
# with hardware:
python -m drinksynth make "iced latte" --port COM4
```
It prints a ticket (what it's building) and the exact machine commands the firmware runs
(`TEMP`, `PUMP id ms`, `ICE`, `WAIT_TEMP`, `DONE`).

## How it works

- [`drinksynth/recipes.py`](drinksynth/recipes.py) — drink library + the ingredient→pump
  map and per-pump flow rates (mL/s).
- [`drinksynth/compiler.py`](drinksynth/compiler.py) — keyword parser → resolved recipe
  (base + temperature + milk + size + extra shot + sweetener) → millilitres converted to
  per-pump run-times → machine command list + human ticket.
- [`firmware/drink_synth.ino`](firmware/drink_synth.ino) — Arduino: pumps via MOSFETs,
  Peltier hot/cold plate via a BTS7960 H-bridge with bang-bang temperature control, NTC
  thermistor, optional servo ice-dropper.

## BOM (~$120, all orderable; reuses the molecular rig's Peltier/Arduino/PSU pattern)

| Part | Role | ~Price |
|---|---|---|
| 5× peristaltic dosing pumps (12 V, silicone tube) | dispense each ingredient | ~$7 ea (~$35) |
| Logic-level MOSFET board (5–8 ch) | switch the pumps from Arduino | ~$10 |
| TEC1-12706 Peltier + BTS7960 H-bridge + heatsink | hot/cold cup plate | ~$30 |
| 100k NTC 3950 thermistor | plate temperature | ~$2 |
| Arduino Uno/Nano | run the recipe | ~$10–27 |
| 12 V 10 A PSU (or the molecular rig's) | power | ~$20 |
| Food-grade silicone tubing + reservoirs/cups | ingredient path | ~$15 |
| (optional) SG90 servo + ice hopper | iced drinks | ~$4 |

**Calibrate** each pump once (time a known volume, set `ml_per_s` in `recipes.py`), use
**food-grade silicone tubing only**, keep electronics dry, and insulate the plate.

## Why it's here

It proves the synthesizer thesis is buildable *now* for one whole domain (drinks), with
the same software pattern and the same cheap repurposed parts as the molecular nanofab —
and it does it honestly: assembly from ingredients, clearly not a matter replicator.
New domains (3D-print router, automated kitchen) can plug into the same request →
compiler → machine pattern as they become cheap and reliable.
