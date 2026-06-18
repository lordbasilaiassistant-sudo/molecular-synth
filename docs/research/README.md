# research dossiers

Full, web-verified background for each subsystem — the raw material behind
[`../science.md`](../science.md) and [`../claims.json`](../claims.json). Each was
researched and then adversarially fact-checked (a second agent tried to refute every
claim and every part's orderability); corrections from that pass are folded into
`claims.json` (e.g. the Aksel-2024 "balance, not 6–30× minimization" framing and the
staple-reuse citation).

> **Background vs. measured experiments.** This folder is the *literature background*. The
> repo-root [`research/`](../../research/) folder holds the *measured, reproducible
> experiments* run against this codebase (Tm validated vs Biopython, folding-buffer salt
> calibration, the physics of scale, the compiler's design levers, and the physics red-team) —
> see [`research/FINDINGS.md`](../../research/FINDINGS.md). Dossiers explain the science we
> built on; `research/` reports what we then measured and found.

| # | file | covers |
|---|---|---|
| 01 | [01-origami-design-tools.md](01-origami-design-tools.md) | DNA origami fundamentals; automated mesh→scaffold routing (caDNAno, vHelix, DAEDALUS, PERDIX/TALOS/METIS, scadnano, oxDNA); the routing algorithm; M13mp18 |
| 02 | [02-folding-thermocycler.md](02-folding-thermocycler.md) | folding reaction (buffer, Mg²⁺, ramp); isothermal folding; the repurposed Peltier/PID thermocycler parts |
| 03 | [03-hardening-inorganic.md](03-hardening-inorganic.md) | DNA → hard inorganic: sol–gel silica (DIY), metal casting (stretch), ALD (service-only) |
| 04 | [04-verification-gel-stm.md](04-verification-gel-stm.md) | DIY agarose gel QC; DIY STM atomic-resolution demonstrator (HOPG, not origami) |
| 05 | [05-bom-consumables.md](05-bom-consumables.md) | consumables + sourcing reality: scaffold, oPool vs plate, buffers, stain, hobbyist purchasability |
| 06 | [06-ai-staple-optimizer.md](06-ai-staple-optimizer.md) | the yield model: SantaLucia Tm, loop-closure balance (Aksel 2024), the implementable optimizer objective |
