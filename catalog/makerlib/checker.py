"""
The Maker Catalog checker.

check(query) answers "can the one system make X, and how?" - it finds the item in
catalog/items.json (by name/alias), or decomposes + classifies an UNKNOWN query
heuristically, and returns a feasibility report. Everything decomposes (item ->
components -> molecules -> atoms; DNA/proteins where biological), every answer is honest
about which rung of the ladder it sits on.

Feasibility ladder (best first):
  ready      a maker in this repo makes it today (watersynth / drinksynth / molsynth)
  assemble   a cheap real-world maker exists (kitchen / 3D printer), not yet integrated
  frontier   demonstrated in a lab, not on a desktop
  north-star not demonstrated at all
"""

from __future__ import annotations

import json
import os

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ITEMS_PATH = os.path.join(_HERE, "items.json")

FEASIBILITY_ORDER = ["ready", "assemble", "frontier", "north-star"]
FEASIBILITY_LABEL = {
    "ready": "READY - a maker in this repo makes it today",
    "assemble": "ASSEMBLE - cheap real-world maker exists, not yet integrated",
    "frontier": "FRONTIER - demonstrated in a lab, not on a desktop",
    "north-star": "NORTH-STAR - not demonstrated; the dream",
}

# keyword -> (feasibility, maker, category, decomposition tail) for UNKNOWN queries
_BUCKETS = [
    (("water", "ice"), ("ready", "watersynth", "drink",
        ["H2O molecules", "atoms"])),
    (("coffee", "tea", "latte", "juice", "soda", "cola", "lemonade", "smoothie",
      "drink", "espresso", "cocktail", "milk"),
        ("ready", "drinksynth", "drink", ["water + dissolved/suspended molecules", "atoms"])),
    (("origami", "nanostructure", "nanoshape", "aptamer", "nanorobot"),
        ("ready", "molsynth", "material", ["DNA scaffold + staples", "nucleotides", "atoms"])),
    (("nano", "dna"),
        ("ready", "molsynth", "material", ["DNA scaffold + staples", "nucleotides", "atoms"])),
    (("cookie", "cake", "bread", "pizza", "pasta", "soup", "meal", "sandwich",
      "snack", "sauce", "dish", "rice", "egg", "food", "candy", "chocolate",
      "lasagna", "taco", "burger", "burrito", "noodle", "fries", "salad", "stew",
      "curry", "omelette", "pancake", "waffle", "muffin", "donut", "pie", "fruit"),
        ("assemble", "kitchen (planned)", "food",
         ["stocked ingredients", "polysaccharides/proteins/lipids/water", "atoms"])),
    (("case", "bracket", "holder", "part", "tool", "toy", "gear", "mount",
      "widget", "clip", "knob", "object", "figurine", "enclosure"),
        ("assemble", "3dprint (planned)", "object",
         ["a 3D mesh of thermoplastic", "polymer (PLA/PETG)", "atoms"])),
    (("protein", "enzyme", "antibody", "peptide", "hormone", "insulin"),
        ("frontier", "biofab (frontier)", "component",
         ["amino-acid chain", "amino acids", "encoded by DNA", "atoms"])),
    (("drug", "molecule", "compound", "medicine", "aspirin", "vitamin", "chemical"),
        ("frontier", "chemfab (frontier)", "component",
         ["a sequence of bond-forming reactions", "atoms + bonds"])),
    (("phone", "smartphone", "computer", "cpu", "chip", "microchip", "battery",
      "circuit", "screen", "transistor", "laptop", "processor"),
        ("north-star", "none", "object",
         ["semiconductors + battery + display", "doped silicon/metals/polymers", "atoms"])),
]


def load_catalog(path=None):
    with open(path or _ITEMS_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _norm(s):
    return s.lower().strip()


def find(query, catalog=None):
    catalog = catalog or load_catalog()
    q = _norm(query)
    items = catalog["items"]
    # exact name / alias
    for it in items:
        if q == _norm(it["name"]) or q in [_norm(a) for a in it.get("aliases", [])]:
            return it
    # substring (query in a name/alias, or name/alias in query)
    for it in items:
        names = [_norm(it["name"])] + [_norm(a) for a in it.get("aliases", [])]
        if any(q in n or n in q for n in names):
            return it
    return None


def best_feasibility(styles):
    feas = [s.get("feasibility", "north-star") for s in styles] or ["north-star"]
    return min(feas, key=lambda f: FEASIBILITY_ORDER.index(f)
               if f in FEASIBILITY_ORDER else len(FEASIBILITY_ORDER))


def classify_unknown(query):
    q = _norm(query)
    for keys, (feas, maker, category, tail) in _BUCKETS:
        if any(k in q for k in keys):
            return {
                "name": query, "category": category, "cataloged": False,
                "decomposition": [query] + tail,
                "styles": [{"style": "estimated", "maker": maker, "feasibility": feas,
                            "how": "(estimated from the nearest known category - add to "
                                   "items.json after checking)", "needs": [], "citation": ""}],
                "best_feasibility": feas,
                "notes": "Not yet cataloged. Estimate from the nearest bucket; verify and add it.",
            }
    return {
        "name": query, "category": "unknown", "cataloged": False,
        "decomposition": [query, "(decompose into components -> molecules -> atoms)"],
        "styles": [{"style": "unknown", "maker": "none", "feasibility": "north-star",
                    "how": "(not classified - decompose it and add to items.json)",
                    "needs": [], "citation": ""}],
        "best_feasibility": "north-star",
        "notes": "Not cataloged and not recognised. Decompose it (the cookie principle) and add it.",
    }


def check(query, catalog=None):
    """Return a feasibility report for `query` (cataloged item or heuristic estimate)."""
    catalog = catalog or load_catalog()
    it = find(query, catalog)
    if it is None:
        return classify_unknown(query)
    return {
        "name": it["name"], "category": it.get("category", ""), "cataloged": True,
        "decomposition": it.get("decomposition", []),
        "styles": it.get("styles", []),
        "best_feasibility": best_feasibility(it.get("styles", [])),
        "notes": it.get("notes", ""),
    }


def list_catalog(catalog=None):
    catalog = catalog or load_catalog()
    out = []
    for it in catalog["items"]:
        out.append({"name": it["name"], "category": it.get("category", ""),
                    "feasibility": best_feasibility(it.get("styles", [])),
                    "makers": sorted({s.get("maker", "?") for s in it.get("styles", [])})})
    return out
