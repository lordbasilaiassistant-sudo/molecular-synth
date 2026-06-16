---
name: Bug report
about: Something the compiler, rig, or synth does wrong
title: ""
labels: bug
---

**What happened**
A clear description of the bug.

**Repro**
- Command / code (e.g. `python -m molsynth compile <shape> --out out`)
- Shape / input file (attach the .stl/.ply/.json if relevant)
- Full output / traceback

**Expected**
What you expected instead.

**Environment**
- OS + Python version
- Optional deps installed (scadnano / trimesh / biopython)?

**Checks**
- [ ] `python tests/test_compiler.py` passes on `main`
- [ ] `python validate/validate.py` still PASSes
