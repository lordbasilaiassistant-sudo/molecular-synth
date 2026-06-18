# integration.md — how every cog fits into one real rig

This is the system view: the final-assembly blueprint that turns the parts of this repo
(compiler → firmware → hardware) into **one nanofab bench you can build**. It covers
control, power, thermal, fluidics, materials, verification, and safety for the
DNA-origami rig — the honest engineering truth behind the one-command pipeline.

## 1. The stack (software → atoms)

```
  SHAPE            preset / STL / PLY / JSON wireframe
        │
        ▼
  COMPILER         compiler/molsynth   (route scaffold · break + optimize staples · emit protocol + 3D)
        │  scaffold.fasta · staples.csv · protocol.md · design.top/conf.dat · screen.md · diagnostics.md
        ▼
  ORDER            M13mp18 scaffold (NEB) + staple oPool (IDT)
        │
        ▼
  FIRMWARE         thermocycler.ino on the rig's microcontroller (serial protocol)
        │  host_ramp.py streams the 90 -> 20 C anneal ramp
        ▼
  HARDWARE         Peltier+PID thermocycler · DIY gel + transilluminator · (optional) DIY STM
        │
        ▼
  VERIFY           a tight folded band on the gel (and optional atomic-resolution STM demo)
```

One shape flows top to bottom: the compiler turns it into orderable oligos + the wet-lab
recipe; the rig folds and verifies it.

## 2. The shared subsystems

| Subsystem | What it is | Real-world notes |
|---|---|---|
| **Control** | a host (PC/Raspberry Pi) runs the compiler and streams the ramp; talks to the rig's microcontroller (Arduino/Teensy) over **USB serial** | the firmware protocol is the contract (`TEMP`, `RAMP`, `STATUS`, `OK`); `host_ramp.py` streams the slow-cool schedule |
| **Power** | one **12 V** rail from a PC/LED PSU, fused | the TEC1-12706 Peltier dominates (~60 W); size the PSU to the thermocycler + control + gel (proven in `proofs/run_proofs.py`) |
| **Thermal** | Peltier + heatsink/fan under PID control | the folding ramp is the core thermal job — slow-cool 90 -> 20 C in ~1-2 h; the gel runs cold |
| **Structure** | a printed/extruded frame; vibration isolation for the optional STM | the parametric CAD (`hardware/cad/*.scad`) prints the thermocycler block, gel box, and STM mount |

## 3. The wetted path (the nanofab, isolated)

DNA reagents and the optional silane/TEOS hardening chemistry are kept in their own
**fume-vented bay**, never crossing kitchen/food paths:

| Stage | Path |
|---|---|
| **Fold** | scaffold + staples in 1x TAE + ~12.5 mM MgCl2, in PCR tubes -> the Peltier thermocycler block |
| **Verify** | the folded reaction -> agarose gel box (1x TAE + Mg) -> blue transilluminator -> a tight band |
| **(Optional) Harden** | sol-gel silica (TEOS + aminosilane + methanol) in the **fume-vented** bay -> rigid SiO2 replica |
| **(Optional) Image** | a DIY STM atomic-resolution demonstrator (on HOPG, the imaging proof-of-capability) |

## 4. Materials in / out

| In (you stock) | Out |
|---|---|
| M13mp18 scaffold (NEB), staple oPool (IDT), Mg buffer | ~10⁹–10¹² nanostructures per reaction (liquid) |
| TEOS / aminosilane / methanol (optional) | rigid silica replicas |

Consumables are the recurring cost (~$570/design on the oPool path); the rig/control/power
are a one-time build (see [`../bom`](../bom)).

## 5. Verification / feedback (closed loop)

- **Did it fold?** the gel box + blue transilluminator — a tight folded band, distinct
  from the scaffold-only lane (a USB camera can image the gel for the host).
- **Atomic imaging (optional):** the DIY STM demonstrator.
- The firmware replies `OK`/`READY` on each step so the host can sequence the ramp and retry.

## 6. Safety (enforced in hardware + firmware)

| Hazard | Control |
|---|---|
| Flammable silanes/alcohols (hardening) | fume-vented bay; keep away from heaters/sparks |
| Hot surfaces | firmware temp caps (`T_MAX`), insulation, lid interlock |
| Electrical (12 V/30 A) | per-rail fuses, correct wire gauge, common ground, e-stop cutting the PSU |
| Gel electrophoresis (60–90 V) | enclosed gel box; use DNA-safe stain (GelGreen/GelRed), not ethidium bromide |
| DNA reagents | non-hazardous (non-pathogenic M13 + short oligos), but kept labelled in the lab bay |

## 7. Final assembly sequence

1. **Frame** — build the chassis; mount the PSU and the host.
2. **Power** — wire the 12 V rail, fuses, common ground, e-stop.
3. **Thermocycler** — build the Peltier+PID block (heatsink -> Peltier -> aluminium tube
   block -> printed collar; BTS7960 H-bridge); flash `thermocycler.ino`; verify `STATUS`/`OK`.
4. **Gel rig** — the printed gel box (or an IVYX gel) + blue transilluminator.
5. **Software** — `python -m molsynth compile <shape>` emits the oligos + protocol + the
   3D structure + the Mg x ramp screen; `host_ramp.py` streams the ramp.
6. **Validate the rig FIRST** — fold a **known published design** and confirm the gel band
   before trusting novel compiled designs (separates rig faults from design faults).
7. **Safety check** — interlocks, fuses, fume vent, e-stop.
8. **First fold** — scaffold ~20 nM + staples 5–10x in Mg buffer; run the 90 -> 20 C ramp;
   gel-verify; view the design in oxView.

That is the whole rig, every cog, top to bottom — honest at each layer: a real
bottom-up nanofab, a clearly-labelled line between what's buildable today and the
[north-star](north-star.md) above it.
