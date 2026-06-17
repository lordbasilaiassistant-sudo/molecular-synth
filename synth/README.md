# /synth — buildable-today synthesizers (Water + Drink + the router)

"I want a glass of cold water." / "Iced oat latte, large, extra shot." → a
request-compiler turns it into a deterministic machine recipe → cheap hardware makes it.
Same architecture as the molecular compiler (request → compiler → machine recipe), at
macroscale, for ~$120–180 of orderable parts. See [`../docs/vision.md`](../docs/vision.md)
for why this is the *real-today* rung of the synthesizer thesis (and what stays
north-star).

## Item Synth — one front door for the whole federation

[`itemsynth/`](itemsynth/) is the **AI request-compiler** of the thesis: ask for *anything*
and it routes the request to the maker that fits — Water, Drink, Print, or the molecular
(DNA) compiler — or, for things no cheap desktop can honestly make today (working
electronics, arbitrary matter from atoms), it returns the **north-star verdict instead of a
faked recipe**. The classifier is a transparent keyword scorer (no LLM, no black box), so
every routing decision explains itself (`route(req)["matched"]`).

```bash
cd synth
python -m itemsynth "a large glass of cold water"     # -> water maker
python -m itemsynth "iced oat latte, large"           # -> drink maker
python -m itemsynth "a phone case"                    # -> print maker
python -m itemsynth "an octahedron DNA nanocage"      # -> molecular compiler (emits a design)
python -m itemsynth "a working smartphone"            # -> honest north-star, not faked
python -m itemsynth --classify-only "matcha latte"    # show the routing decision only
```
```python
from itemsynth import route
r = route("a large glass of cold water")
print(r["maker"], r["recipe"])     # 'water' -> ['HARVEST 400 ...', 'FILTER ...', 'DISPENSE 400 ...']
```

Two makers live here, sharing the pattern:
- **Water Synth** ([`watersynth/`](watersynth/)) — harvests water from **air** (Peltier
  condensation / AWG), filters + UV-treats it, dispenses. The most tractable "ask → it
  appears" of all, and genuinely humanity-useful (clean water from air).
- **Drink Synth** ([`drinksynth/`](drinksynth/)) — pumps + hot/cold plate assemble a
  drink from stocked ingredients.

> **Honest scope:** these **harvest/assemble and treat** from air or stocked ingredients.
> They do **not** synthesise matter from energy. The lived experience ("ask, it appears")
> is real and cheap today; materialising matter from energy stays north-star.

## Water Synth

```bash
cd synth
python -m watersynth make "large glass of cold water"
python -m watersynth make "hot water"
python -m watersynth make "water" --reservoir   # dispense from a tank, skip air-harvest
python -m watersynth make "cold water" --port COM5   # with hardware
```
Emits `HARVEST · FILTER · UV · TEMP · DISPENSE · DONE`. Firmware:
[`firmware/water_synth.ino`](firmware/water_synth.ino).

**Water Synth BOM (~$60–90, reuses the molecular rig's Peltier):**

| Part | Role | ~Price |
|---|---|---|
| TEC1-12706 Peltier + heatsinks + fan | condense water from air (cold plate) | ~$25 |
| Activated-carbon inline filter | taste / VOC | ~$8 |
| UV-C LED + driver | sterilise collected water | ~$12 |
| Peristaltic pump + food-grade tubing | dispense | ~$10 |
| 2nd Peltier + BTS7960 (serving temp) | hot/cold the cup | ~$20 |
| 100k NTC thermistor + Arduino + 12 V PSU | control (or share the molecular rig's) | ~$15 |

> Condensation rate is humidity-dependent (~tens of mL/hour on a small Peltier; MOF
> desiccants raise yield in dry air — Kim et al., *Science* 2017). Use a buffer tank so
> dispense is instant. Sterilise (UV-C) before drinking; UV-C is an eye/skin hazard —
> fully enclose it.

## Drink Synth

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
