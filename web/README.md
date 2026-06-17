# /web — the browser 3D sim (GitHub Pages)

A self-contained Three.js simulation of the **water module** making a clean glass of
water in seconds. Deployed to GitHub Pages from this folder (`.github/workflows/pages.yml`):

**Live:** https://lordbasilaiassistant-sudo.github.io/molecular-synth/

It's a *sim to design/test the real machine*: the machine constants are at the top of
[`index.html`](index.html) (glass volume, valve rate, UV-C dose, buffer, AWG rate), and
the on-screen proof readout shows volume, elapsed time, **UV-C dose** (✓ at ≥40 mJ/cm²,
the 4-log bacteria drinking-water standard), temperature, and buffer level.

**Honest model:** the glass is valve-dispensed (~42 mL/s) from a treated, pre-chilled
buffer that is filled from a **tap/reservoir (instant)** or, off-grid, by the slow Peltier
**atmospheric-water-generator** (~0.1–0.3 L/hr) — so it never depends on humidity. Dispense
is seconds; air-harvest is the slow background. This harvests + treats + dispenses water;
it does not synthesise matter.

Run locally: open `index.html` in a browser (no build step; Three.js from CDN).
