# Contributing to Molecular Synth

Thanks for helping build the synthesizer. This project has one non-negotiable rule that
makes it different: **honesty about what is real.**

## The honesty discipline (read first)

- Every *capability* claim must cite a **real, experimentally-demonstrated** paper, added
  to [`docs/claims.json`](docs/claims.json) with `demonstrated: true`, `track: buildable`.
- Anything not demonstrated (diamondoid mechanosynthesis, macroscopic replication) goes on
  the **north-star** track (`demonstrated: false`, `track: north-star`) — never in the BOM,
  never implied as buildable. See [`docs/north-star.md`](docs/north-star.md) and
  [`docs/vision.md`](docs/vision.md).
- Every BOM line must be **orderable online today** with a live link + price; the rig
  subtotal stays **< $1500**.
- The gate enforces this. A change that breaks it does not merge.

## Run it locally

```bash
# compiler tests (pure stdlib, no installs)
python tests/test_compiler.py
# drink-synth tests
python synth/tests/test_drinksynth.py
# the validate gate (sourceable AND demonstrated, rig < $1500)
python validate/validate.py
# end-to-end smoke
cd compiler && python -m molsynth compile tetrahedron --out /tmp/tetra
```
CI runs all of the above on every push (`.github/workflows/ci.yml`).

## Code conventions

- Core compiler path is **standard-library only** — keep it dependency-free so
  `python -m molsynth compile <shape>` works with zero installs. Put optional integrations
  (scadnano, trimesh, biopython) behind `try/except`.
- Match the surrounding style; keep functions small and commented where the science needs it.
- Add a test for new behaviour. Numerics should be **anchored to the literature**, not to
  ourselves (see `TestScience` in `tests/test_compiler.py`).
- If you add a BOM part or a claim, update `bom/bom.json` / `docs/claims.json` and run
  `python bom/render_bom.py` + `python validate/validate.py`.

## Workflow

1. Pick an issue (good-first-issue labels are a friendly start) or open one.
2. Branch, implement, add tests, run the suite + the gate.
3. Open a PR referencing the issue (`Closes #N`). The PR template asks you to confirm the
   gate passes and the honesty rules hold.

By contributing you agree your work is MIT-licensed (see [`LICENSE`](LICENSE)).
