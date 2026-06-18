# /web — the project landing page (GitHub Pages)

A self-contained, dependency-free landing page for **Molecular Synth** — the desktop
DNA-origami nanofactory. Deployed to GitHub Pages from this folder
(`.github/workflows/pages.yml`):

**Live:** https://lordbasilaiassistant-sudo.github.io/molecular-synth/

Tabs:
- **Overview** — what the machine is, the headline numbers, and how a request becomes matter.
- **What it makes** — a live Three.js DNA-origami wireframe nanostructure, plus the three
  outputs (shapes · functionalised · hardened). Atomic precision, nanoscale.
- **Blueprint & parts** — the parts table + build phases, rendered live from the repo's
  single-source `bom.json` (`data/bom.json`, the same file the validate gate checks).
- **The vision** — the honest "what's real vs north-star" table and the research ladder from
  DNA origami toward molecular manufacturing.

Pure HTML + a little Three.js (from CDN) — no build step, no framework. `pages.yml` stages
`bom/bom.json` into `data/` at deploy time so the blueprint table stays in sync with the repo.
Run locally: open `index.html` in a browser.
