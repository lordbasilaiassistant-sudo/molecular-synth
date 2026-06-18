# /examples

Sample inputs and committed sample outputs (benign DNA sequences — safe to read).

## Inputs
- presets: `tetrahedron`, `cube`, `octahedron`, `square` (built into the compiler)
- [`square_pyramid.json`](square_pyramid.json) — a non-preset wireframe spec
  (`vertices` + `edges`), to show custom-shape input

## Committed outputs (regenerate any time)
- `out_tetrahedron/`, `out_cube/`, `out_octahedron/`, `out_square_pyramid/`

Each was produced with, e.g.:
```bash
cd compiler
python -m molsynth compile cube --out ../examples/out_cube --iterations 8000
python -m molsynth compile ../examples/square_pyramid.json --out ../examples/out_square_pyramid
```

Open `out_cube/protocol.md` to see the auto-emitted wet-lab recipe, `staples.csv` for
the orderable oligos, and `design.json` for the full design. `diagnostics.md` carries the
per-design yield report plus the **Physics & materials reality check** (edge stiffness,
G-quadruplex audit, buffer-accurate Tm, kinetic caveat). These are illustrative; the
synthetic-vs-real-M13 scaffold is noted in each output's header.

> Note: these committed snapshots predate the latest diagnostics section; regenerate with the
> commands above to see the current reality-check output (the orderable oligos are unchanged).
