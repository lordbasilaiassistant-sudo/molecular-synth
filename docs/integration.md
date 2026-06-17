# integration.md — how every cog fits into one real machine

This is the system view: the final-assembly blueprint that turns the parts of this repo
(brain → catalog → maker compilers → firmware → hardware) into **one chassis you can
build**. It covers every aspect — control, power, thermal, fluidics, materials, safety,
scheduling — and states the honest engineering truth the Orville fantasy hides:
**one brain, one chassis, but physically separate wetted modules.**

## 1. The stack (software → atoms)

```
  VOICE / TEXT  ("whiskey on the rocks")
        │  speech-to-text adapter (browser Web Speech / whisper) — optional
        ▼
  ORDER BRAIN        catalog/makerlib/order.py   (rule-based + LLM hook)
        │  structured intent
        ▼
  MAKER CATALOG      catalog/items.json          (decompose · feasibility · route)
        │  "route to: watersynth + drinksynth"
        ▼
  MAKER COMPILERS    molsynth | drinksynth | watersynth   (request → machine recipe)
        │  machine commands (ICE 80 | PUMP whiskey 60 | DONE)
        ▼
  FIRMWARE           *.ino on each module's microcontroller (serial protocol)
        │  PWM / GPIO
        ▼
  HARDWARE           Peltiers · pumps · UV-C · heaters · sensors  → the cup / the tube
```

One request flows top to bottom; the brain may fan one order across **several modules**
(ice from the water module + pour from the bar module = "on the rocks").

## 2. The four things every module shares

| Shared subsystem | What it is | Real-world notes |
|---|---|---|
| **Control** | one host (Raspberry Pi) runs brain+catalog+compilers; talks to each module's microcontroller (Arduino/Teensy) over **USB serial** | one job scheduler; one serial line per module; the firmware protocol is the contract (`ICE`, `PUMP`, `TEMP`, `HARVEST`, `STEP`…) |
| **Power** | one **12 V** rail from a PC/LED PSU, fused per module | Peltiers dominate (TEC1-12706 ≈ 60 W each); size the PSU to the **simultaneously-active** modules, not the sum; common ground |
| **Thermal** | Peltiers + heatsinks/fans; hot & cold | **the key constraint:** a Peltier doing the thermocycler ramp can't also freeze ice at the same instant → the scheduler serialises thermal jobs (§7) |
| **Structure** | one printed/extruded-frame chassis with module **bays**; vibration isolation for the optional STM | modules slot in; share the frame, PSU, and host, nothing wetted |

## 3. The wetted modules (PHYSICALLY ISOLATED — the honest truth)

You **cannot** share a cup or a fluid path between whiskey, drinking water, and
DNA/silane reagents. Food safety + cross-contamination + UV/flammable hazards force
**separate wetted modules** in the one chassis:

| Module | Makes | Wetted path | Must NOT share with |
|---|---|---|---|
| **Water** (`watersynth`) | water, ice | air-condenser → carbon filter → UV-C → food-grade tubing → cup | lab reagents |
| **Bar/Drink** (`drinksynth`) | coffee, cocktails | spirit/mixer reservoirs → peristaltic pumps → food-grade tubing → cup | lab reagents |
| **Nanofab** (`molsynth`) | DNA/silica nanostructures | PCR tubes → thermocycler block; silane/TEOS in a **fume-vented** bay; gel box | the food/drink cups, the kitchen |
| **Kitchen** (planned) | cookie, bread | ingredient dosers → mixer → oven | lab reagents |
| **3D print** (planned, #8) | objects | filament → hot end (dry) | n/a (not wetted) |

> **This is the integration truth:** "one machine that makes anything" = **one brain +
> one chassis + shared power/control**, routing to the **right isolated module**. The
> single-slot Orville illusion is approximated by one UI + one cup-presentation bay the
> active food/drink module dispenses into — never the lab module.

## 4. Fluidics (the bar/water side)

- **Reservoirs:** water tank, spirit bottles, mixer bottles — each on its own pump.
- **Pumps:** one peristaltic pump per ingredient (the synth scales with pump count);
  food-grade silicone tubing only.
- **Dispense head:** all food/drink tubing converges over the **cup bay**; the cup sits
  on a Peltier plate (serving temperature) with a load cell (fill level).
- **Ice:** the water module freezes machine-made water and drops cubes into the cup
  (servo hopper) before the pour — that's "on the rocks."
- **Cleaning (CIP):** a water+sanitiser flush cycle through the food tubing between
  different drinks (the brain inserts a `FLUSH` step on ingredient change).

## 5. Materials in / out (cartridges)

| In (you stock) | For | Out |
|---|---|---|
| water tank / humid air | water module | a glass of water / ice |
| spirits, mixers, coffee concentrate, milk | bar module | a drink |
| M13 scaffold, staple oPools, Mg buffer, TEOS/silane | nanofab | ~10⁹–10¹² nanostructures (liquid), silica replicas |
| ingredient cartridges | kitchen | a cookie/loaf |
| filament/resin | 3D print | an object |

Consumables are the recurring cost; the chassis/control/power are one-time (see
[`../bom`](../bom)).

## 6. Verification / feedback (closed loop)

- Drink/water: temperature (NTC), fill (load cell), flow timing → the firmware confirms each step.
- Nanofab: the **gel box + blue transilluminator** (did it fold?) and the optional DIY
  STM (atomic-resolution demo); a USB camera images the gel/cup for the host.
- Every firmware step replies `OK`/`READY` so the host can sequence and retry.

## 7. Scheduling / orchestration (one brain, shared resources)

The host runs a **job queue**. Rules that fall out of the shared subsystems:
- **Thermal exclusivity:** only one Peltier-heavy job per shared Peltier at a time
  (don't freeze ice mid-thermocycler-ramp). Modules with their own Peltier run in parallel.
- **Power ceiling:** the scheduler never activates modules whose combined draw exceeds
  the PSU; it serialises instead.
- **Fluid isolation:** a food/drink order and a nanofab run never share tubing or cup;
  they can run concurrently only because they're separate modules.
- **Cleaning gates:** `FLUSH` between incompatible drinks.

## 8. Safety (every aspect, enforced in hardware + firmware)

| Hazard | Control |
|---|---|
| UV-C (water steriliser) | fully enclosed; interlock kills UV if the bay opens |
| Flammable silanes/alcohols (nanofab hardening) | fume-vented bay; keep away from heaters/sparks |
| Hot surfaces / boiling | firmware temp caps (`T_MAX`), insulation, lid interlock |
| Electrical (12 V/30 A) | per-module fuses, correct wire gauge, common ground, e-stop cutting PSU |
| Food contact | food-grade tubing only; CIP flush; lab and food paths never cross |
| DNA reagents | non-hazardous, but kept in the isolated lab bay; label everything |

## 9. Final assembly sequence (the build order)

1. **Frame** — build the chassis with module bays; mount the PSU and the host (Pi).
2. **Power** — wire the 12 V rail, per-module fuses, common ground, e-stop.
3. **Control** — flash each module's microcontroller; connect over USB; verify the serial
   protocol (`STATUS`/`OK`) for each.
4. **Modules** — install water, bar, nanofab modules in their bays; plumb food-grade
   tubing to the cup bay; vent the nanofab bay.
5. **Software** — install the host stack (`molsynth`, `drinksynth`, `watersynth`,
   `makerlib`); wire the order brain; (optional) add the voice adapter + LLM key.
6. **Calibrate** — pump flow rates (`ml_per_s`), thermistor offsets, ice yield, the
   thermocycler ramp; run each module's self-test.
7. **Safety check** — interlocks, fuses, fume vent, UV enclosure, e-stop.
8. **First end-to-end order** — say *"whiskey on the rocks"* → watch ICE (water module) +
   POUR (bar module) compose into one cup. Then *"compile a tetrahedron"* → nanofab.

## 10. Worked example: "whiskey on the rocks" through the whole stack

```
voice → "whiskey on the rocks"
brain  interpret() → {ice:true, pour:{whiskey:60}}           (catalog/makerlib/order.py)
plan   ICE 80 (watersynth) | PUMP whiskey 60 (drinksynth) | DONE
sched  thermal: water module's own Peltier freezes ice; bar pump independent → parallel ok
fw     water-module: HARVEST/freeze + drop cube;  bar-module: pump 60 mL into the cup bay
out    a glass of ice with whiskey, in the one presentation bay
```

That is the whole machine, every cog, top to bottom — and it's honest at each layer:
real makers, isolated fluid paths, one brain, and a clearly-labelled line between what's
buildable today and the [north-star](north-star.md) above it.
