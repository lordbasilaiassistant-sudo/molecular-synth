# north-star.md — the part that is NOT buildable yet

This file exists so the ambition has a home that can **never be confused with the
buildable rig**. Everything here is `demonstrated: false`, `track: north-star` in
[`claims.json`](claims.json), and is excluded from the BOM and from `/validate`'s
"sourceable" accounting.

## The dream: diamondoid mechanosynthesis

Drexler's vision is **positional covalent assembly**: a stiff molecular tooltip places
individual carbon atoms at programmed coordinates to build atomically-precise diamond
(and other stiff covalent solids) — a "matter compiler" that outputs macroscopic,
load-bearing parts. `[ns-diamondoid-mechanosynthesis]`, `[ns-macroscopic-apm]`.

## Why it is north-star, not buildable

- **It has never been experimentally demonstrated.** The supporting literature is
  **DFT / molecular-dynamics simulation only** — tooltip reaction-energetics studies,
  proposed minimal toolsets, reaction-pathway calculations. No lab has positionally
  deposited carbon to build a designed diamond structure.
  - Drexler, K.E. *Nanosystems: Molecular Machinery, Manufacturing, and Computation*
    (Wiley, 1992).
  - Freitas, R.A. & Merkle, R.C. *A Minimal Toolset for Positional Diamond
    Mechanosynthesis.* J. Comput. Theor. Nanosci. 5, 760 (2008). (DFT.)
- **The hard, unsolved physics:** tooltip fabrication and recharging, error-free
  single-atom placement against thermal noise, the immense **operation count**
  (below), and side-reaction control. These are open problems, not engineering details.

## Make the scale concrete (geometry-only simulation)

[`/northstar/diamond_sim.py`](../northstar/diamond_sim.py) is a deliberately honest toy:
it places carbon atoms on a **diamond-cubic lattice** inside a target box and writes an
`.xyz` file you can open in any molecular viewer. **It simulates only the GEOMETRY of a
positionally-assembled diamond — it does not simulate the mechanosynthesis chemistry,
which is the unsolved part.** Its real output is the *operation budget*: e.g. building a
1 mm³ diamond block is ~1.76 × 10²⁰ atoms, which at an optimistic 1 MHz single-tooltip
placement rate is millions of years — the number that tells you why this is north-star
and why massive parallelism (or a wholly different approach) is mandatory before it is
real.

```
python northstar/diamond_sim.py --nm 5 --out northstar/out/diamond_5nm.xyz
```

## A second, independent reason it's hard (the physics of scale)

The operation-count above is the *throughput* wall. There is also a *force* wall:
macroscopic atom-up assembly fights physics that re-sorts with size. Below ~0.8 µm, thermal
motion dominates and matter can assemble itself; above it, gravity and contact forces take
over and self-assembly stops — you need a fundamentally different mechanism. The manipulation
sweet spot (~10 nm–0.8 µm) is exactly the DNA-origami window, and the route upward is
**hierarchical** assembly (compose scales), not a single tooltip placing 10²⁰ atoms. The
computed crossover scales are in [`../research/FINDINGS.md`](../research/FINDINGS.md) (exp 2 & 5).
Both walls point the same way: parallelism + hierarchy, or a wholly different approach.

## The honest bridge from the buildable track

The buildable rig already does **programmable, sequence-addressed self-assembly** and
**templated conversion to a hard inorganic** (silica/metal). That is genuine
bottom-up atomically-*defined* manufacturing at the nanoscale — a real rung on the
ladder. It is **not** positional covalent mechanosynthesis, and this repository never
claims it is. The north-star stays simulated and labelled until someone demonstrates
the chemistry; the rig ships on what is already real.
