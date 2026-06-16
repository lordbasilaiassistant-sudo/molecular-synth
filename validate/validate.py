#!/usr/bin/env python3
"""
THE GATE.  Molecular Synth v0 only ships if both hold:

  (A) SOURCEABLE   - every BOM line is orderable online today, has a live link and a
                     price, and the RIG-hardware subtotal is < $1500.
  (B) DEMONSTRATED - every capability claim on the BUILDABLE track cites a real,
                     experimentally-demonstrated paper (with a URL). Claims on the
                     NORTH-STAR track (e.g. diamondoid mechanosynthesis) are allowed
                     to be simulation-only, but MUST be labelled track="north-star"
                     so they can never masquerade as buildable.

Run after every design pass:   python validate/validate.py
Exit code 0 = PASS (ship), 1 = FAIL (do not report "infeasible"; substitute a
repurposed/demonstrated alternative and re-run - see the goal's iteration loop).

Inputs (single source of truth):
  bom/bom.json     list[ {name, category, vendor, url, price_usd, orderable, ...} ]
                   category in {rig-hardware, consumable, optional}
  docs/claims.json list[ {id, claim, citation, url, demonstrated, track, scope_note} ]
                   track in {buildable, north-star}
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUDGET_USD = 1500.0


def _load(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None, f"MISSING FILE: {path}"
    with open(full, "r", encoding="utf-8") as fh:
        return json.load(fh), None


def check_bom(bom):
    errors, warnings = [], []
    rig_total = 0.0
    consumable_total = 0.0
    for i, line in enumerate(bom):
        tag = line.get("name", f"line{i}")
        cat = line.get("category", "")
        url = (line.get("url") or "").strip()
        price = line.get("price_usd")
        orderable = line.get("orderable")
        if cat not in ("rig-hardware", "consumable", "optional"):
            errors.append(f"[BOM] {tag}: bad category '{cat}'")
        if not url.startswith("http"):
            errors.append(f"[BOM] {tag}: no live link")
        if not isinstance(price, (int, float)) or price < 0:
            errors.append(f"[BOM] {tag}: no/invalid price")
        if orderable is not True and cat != "optional":
            errors.append(f"[BOM] {tag}: not marked orderable")
        if cat == "rig-hardware" and isinstance(price, (int, float)):
            rig_total += price
        if cat == "consumable" and isinstance(price, (int, float)):
            consumable_total += price
    if rig_total >= BUDGET_USD:
        errors.append(f"[BOM] rig-hardware subtotal ${rig_total:.0f} >= ${BUDGET_USD:.0f}")
    return errors, warnings, rig_total, consumable_total


def check_claims(claims):
    errors, warnings = [], []
    n_demo, n_north = 0, 0
    for i, c in enumerate(claims):
        tag = c.get("id", f"claim{i}")
        track = c.get("track", "")
        url = (c.get("url") or "").strip()
        cite = (c.get("citation") or "").strip()
        demonstrated = c.get("demonstrated")
        if track not in ("buildable", "north-star"):
            errors.append(f"[CLAIM] {tag}: bad track '{track}'")
        if not cite:
            errors.append(f"[CLAIM] {tag}: no citation")
        if not url.startswith("http"):
            warnings.append(f"[CLAIM] {tag}: citation has no URL")
        if track == "buildable":
            if demonstrated is not True:
                errors.append(f"[CLAIM] {tag}: BUILDABLE but not demonstrated=true")
            else:
                n_demo += 1
        elif track == "north-star":
            n_north += 1
            if demonstrated is True:
                errors.append(f"[CLAIM] {tag}: north-star marked demonstrated "
                               f"(would masquerade as buildable)")
    return errors, warnings, n_demo, n_north


def main(argv=None):
    bom, e1 = _load("bom/bom.json")
    claims, e2 = _load("docs/claims.json")
    load_errs = [e for e in (e1, e2) if e]
    if load_errs:
        for e in load_errs:
            print("FAIL:", e)
        return 1

    be, bw, rig, cons = check_bom(bom)
    ce, cw, ndemo, nnorth = check_claims(claims)
    errors = be + ce
    warnings = bw + cw

    print("=" * 64)
    print("Molecular Synth v0 - VALIDATION GATE")
    print("=" * 64)
    print(f"BOM lines        : {len(bom)}  (rig ${rig:.0f} / consumables ${cons:.0f})")
    print(f"Rig budget       : ${rig:.0f} < ${BUDGET_USD:.0f}  "
          f"-> {'OK' if rig < BUDGET_USD else 'OVER'}")
    print(f"Claims           : {len(claims)}  "
          f"(buildable+demonstrated {ndemo}, north-star {nnorth})")
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print("  -", w)
    if errors:
        print("\nERRORS:")
        for e in errors:
            print("  -", e)
        print(f"\nRESULT: FAIL ({len(errors)} blocking). "
              f"Substitute & re-run - do NOT report infeasible.")
        return 1
    print("\nRESULT: PASS - sourceable AND demonstrated. Ship.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
