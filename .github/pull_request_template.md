## What this does

<!-- one or two sentences; link the issue, e.g. Closes #N -->

## Checklist

- [ ] `python tests/test_compiler.py` passes
- [ ] `python synth/tests/test_drinksynth.py` passes (if touched)
- [ ] `python validate/validate.py` PASSes (rig < $1500, claims demonstrated)
- [ ] New numerics are anchored to the literature (cite it) and have a test
- [ ] Honesty rules hold: new capability claims cite a demonstrated paper and are on the
      `buildable` track in `docs/claims.json`; anything not demonstrated is on `north-star`
- [ ] If BOM/claims changed: ran `python bom/render_bom.py`

## Notes

<!-- anything reviewers should know; scope limits stated honestly -->
