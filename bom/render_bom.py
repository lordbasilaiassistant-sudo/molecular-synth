#!/usr/bin/env python3
"""Render bom/bom.json into a human-readable bom/bom.md. Single source of truth =
bom.json (also what validate/validate.py checks). Run: python bom/render_bom.py"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    with open(os.path.join(HERE, "bom.json"), "r", encoding="utf-8") as fh:
        bom = json.load(fh)

    cats = {"rig-hardware": [], "consumable": [], "optional": []}
    for line in bom:
        cats.get(line["category"], cats["optional"]).append(line)

    def table(rows):
        out = ["| Part | Role | Repurposed from | Vendor | Price | Link |",
               "|---|---|---|---|---|---|"]
        for r in rows:
            out.append(
                f"| {r['name']} | {r.get('role','')} | {r.get('repurposed_from','')} "
                f"| {r.get('vendor','')} | ${r['price_usd']:.0f} | [link]({r['url']}) |")
        return "\n".join(out)

    rig = sum(r["price_usd"] for r in cats["rig-hardware"])
    cons = sum(r["price_usd"] for r in cats["consumable"])

    md = f"""# Bill of Materials — Molecular Synth v0

_Auto-generated from [`bom.json`](bom.json) by `render_bom.py` (the same file the
[validation gate](../validate/validate.py) checks). Prices are snapshot estimates
(USA, 2026-06); treat as ±20% and verify at order time._

## Totals
- **Rig hardware: ${rig:.0f}**  (target < $1500 — {'PASS' if rig < 1500 else 'OVER'})
- **Core consumables (per design): ${cons:.0f}**  (staple oPool path; addressable plate adds ~$550)
- Optional tracks (STM, silica hardening, sous-vide) are listed separately and not in the rig total.

## Rig hardware (durable, the < $1500 rig)
{table(cats['rig-hardware'])}

## Consumables (per design / reusable starter kit)
{table(cats['consumable'])}

## Optional (alternative + stretch-track parts)
{table(cats['optional'])}

---
_Honesty notes: search-URL lines (CPU cooler, filament, PEG, pipette set, sous-vide)
point at a live orderable category rather than one SKU — pick any reputable listing.
The compiler emits both an oPool order (`staples_opool.txt`, ~$200) and an addressable
plate order (`staples_idt_plate.txt`, ~$750); choose your cost point._
"""
    with open(os.path.join(HERE, "bom.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(md)
    print(f"wrote bom.md  (rig ${rig:.0f}, consumables ${cons:.0f}, {len(bom)} lines)")


if __name__ == "__main__":
    main()
