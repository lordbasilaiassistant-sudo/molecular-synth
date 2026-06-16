# Folding screen - octahedron

Run this 25-condition screen ONCE on a new design; read the winner off the gel
(tightest, fastest single band vs the scaffold-only lane). Then fold production batches
at the winning MgCl2 x strategy.

Each well: scaffold 20 nM + staples 10x
in 1x TAE + the row's MgCl2, ~20 uL.

| Well | MgCl2 (mM) | Thermal strategy |
|------|-----------|------------------|
| A1 | 5 | ramp 90->20 (2h) |
| A2 | 8 | ramp 90->20 (2h) |
| A3 | 12.5 | ramp 90->20 (2h) |
| A4 | 16 | ramp 90->20 (2h) |
| A5 | 20 | ramp 90->20 (2h) |
| B1 | 5 | ramp 65->25 (16h) |
| B2 | 8 | ramp 65->25 (16h) |
| B3 | 12.5 | ramp 65->25 (16h) |
| B4 | 16 | ramp 65->25 (16h) |
| B5 | 20 | ramp 65->25 (16h) |
| C1 | 5 | isothermal 50C |
| C2 | 8 | isothermal 50C |
| C3 | 12.5 | isothermal 50C |
| C4 | 16 | isothermal 50C |
| C5 | 20 | isothermal 50C |
| D1 | 5 | isothermal 55C |
| D2 | 8 | isothermal 55C |
| D3 | 12.5 | isothermal 55C |
| D4 | 16 | isothermal 55C |
| D5 | 20 | isothermal 55C |
| E1 | 5 | isothermal 60C |
| E2 | 8 | isothermal 60C |
| E3 | 12.5 | isothermal 60C |
| E4 | 16 | isothermal 60C |
| E5 | 20 | isothermal 60C |

How to run each strategy on the rig (hardware/firmware):
- `ramp ...`  -> `python hardware/firmware/host_ramp.py --design design.json --port <COM>`
  (edit `--t-hot/--t-cold/--anneal-min` when you recompile, or step a sous-vide bath).
- `isothermal T` -> hold the block at T (firmware `SET <T>`) for 1-4 h, then cool.

Gel-score every well together (run cold, 1x TAE + ~11 mM MgCl2, 60-90 V). The
condition with the sharpest monomer band wins.
