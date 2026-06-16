# /protocol — the auto-emitted wet-lab recipe

There is no static protocol here: the compiler **emits a recipe per design** into
`<outdir>/protocol.md`, parameterised by that design (scaffold, staple count and
concentration, Mg²⁺ buffer, and the exact anneal ramp the firmware will run). This
keeps the software, the protocol, and the hardware in lock-step — the ramp table in
`protocol.md` is byte-for-byte what `firmware/host_ramp.py` streams to the Arduino.

See a real one: [`../examples/out_cube/protocol.md`](../examples/out_cube/protocol.md).

## The recipe always covers

1. **Order** — scaffold (M13mp18), the staple set (oPool *or* addressable plate), and
   folding buffer (1× TAE + 12.5 mM MgCl₂).
2. **Assemble** — scaffold ~20 nM + staples at 5–10× excess in the Mg²⁺ buffer.
3. **Anneal** — the per-design ramp (heat ~90 °C → slow-cool ~20 °C); run on the
   Peltier/PID block, a programmable thermocycler, or a sous-vide bath.
4. **Verify** — agarose gel (Mg²⁺ in the buffer, 60–90 V, cold); look for the tight
   folded band vs. the scaffold-only control.
5. **(Optional) Purify** — PEG-8000 precipitation or a 100 kDa spin filter.
6. **(Optional) Harden** — sol–gel silicification (TEOS + aminosilane) → rigid SiO₂.
7. **(Optional) Atomic check** — DIY STM on HOPG (capability demo, not origami QC).

## Provenance

Every step is grounded in the canonical protocols — Rothemund (2006), Castro et al.
*Nat. Methods* (2011), Wagenbauer et al. *ChemBioChem* (2017) — see
[`../docs/science.md`](../docs/science.md) §4–6 and the dossiers in
[`../docs/research/`](../docs/research/). Default numbers (12.5 mM Mg²⁺ for 2D; 5–10 mM
wireframe; 16–20 mM dense 3D; 5–10× staple excess) are overridable per design via the
compiler's flags.

> Scope reminder: a folding reaction yields ~10⁹–10¹² copies of a single ~tens-of-nm
> nanostructure. It does not build macroscopic parts.
