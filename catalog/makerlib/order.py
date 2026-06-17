"""
The order brain: natural language -> structured order -> cross-maker fulfillment plan.

"whiskey on the rocks" -> a glass of ICE (watersynth freezes machine-made water) +
WHISKEY poured (drinksynth-style pump). Understands cocktail slang + modifiers (on the
rocks / neat / up / double / tall / dirty), and falls back to the Maker Catalog for
anything non-drink (cookie, water, nanostructure...).

Rule-based by default; an LLM hook (`llm=callable`) lets a real AI/voice front end parse
arbitrary phrasing - the Orville "just ask" experience. The voice layer is an input
adapter (speech-to-text -> this function); see catalog/README.md.

Honest scope: assembles from stocked spirits/mixers + machine-made ice. It does not
synthesise alcohol or food from atoms.
"""

from __future__ import annotations

import json
import os

from .checker import check as catalog_check

_HERE = os.path.dirname(os.path.abspath(__file__))
_KB_PATH = os.path.join(_HERE, "cocktails.json")
ICE_GRAMS = 80
DEFAULT_SPIRIT_ML = 60


def load_cocktails(path=None):
    with open(path or _KB_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _norm(s):
    return " ".join(s.lower().strip().split())


def _merge_mod(acc, m):
    for k, v in m.items():
        if k == "add":
            acc.setdefault("add", {}).update(v)
        else:
            acc[k] = v


def interpret(text, llm=None, kb=None, catalog=None):
    """Resolve free-form text to a structured order intent."""
    kb = kb or load_cocktails()
    raw = _norm(text)

    if llm:                       # optional real-AI parse (returns a phrase or an intent dict)
        try:
            res = llm(raw)
            if isinstance(res, dict):
                return res
            if isinstance(res, str) and res.strip():
                raw = _norm(res)
        except Exception:
            pass

    t = kb["aliases"].get(raw, raw)
    spirits = set(kb["spirits"])

    # collect modifier overrides (longest phrase first so "straight up" beats "up")
    mods, found = {}, []
    for phrase in sorted(kb["modifiers"], key=len, reverse=True):
        if phrase in t:
            _merge_mod(mods, kb["modifiers"][phrase])
            found.append(phrase)

    # recipe match on the alias-resolved text (longest name first)
    recipe, rname = None, None
    if t in kb["recipes"]:
        recipe, rname = kb["recipes"][t], t
    else:
        for name in sorted(kb["recipes"], key=len, reverse=True):
            if name in t:
                recipe, rname = kb["recipes"][name], name
                break

    if recipe is None:            # bare spirit? ("whiskey neat", "a double vodka")
        cleaned = t
        for p in found:
            cleaned = cleaned.replace(p, " ")
        cleaned = _norm(cleaned)
        spirit = next((s for s in kb["spirits"] if s in cleaned), None)
        if spirit:
            recipe = {"pour": {spirit: DEFAULT_SPIRIT_ML}, "ice": False, "garnish": ""}
            rname = spirit

    if recipe is None:            # not a drink -> route to the Maker Catalog
        rep = catalog_check(text, catalog)
        return {"kind": "catalog", "name": rep["name"], "raw": text,
                "report": rep, "feasibility": rep["best_feasibility"]}

    pour = dict(recipe.get("pour", {}))
    ice = recipe.get("ice", False)
    chilled = recipe.get("chilled", False)
    garnish = recipe.get("garnish", "")
    mixer = True

    if "ice" in mods:
        ice = mods["ice"]
    if "chilled" in mods:
        chilled = mods["chilled"]
    if mods.get("mixer") is False:
        mixer = False
        pour = {k: v for k, v in pour.items() if k in spirits}
    if "spirit_mult" in mods:
        for k in list(pour):
            if k in spirits:
                pour[k] = round(pour[k] * mods["spirit_mult"])
    if "mixer_mult" in mods:
        for k in list(pour):
            if k not in spirits:
                pour[k] = round(pour[k] * mods["mixer_mult"])
    for k, v in mods.get("add", {}).items():
        pour[k] = v

    return {"kind": "drink", "name": rname, "raw": text, "pour": pour, "ice": ice,
            "chilled": chilled, "garnish": garnish, "mixer": mixer,
            "modifiers": found, "feasibility": "ready"}


def fulfill(intent):
    """Turn an intent into a cross-maker plan: ordered steps + machine commands."""
    if intent["kind"] == "catalog":
        rep = intent["report"]
        makers = sorted({s["maker"] for s in rep["styles"]})
        ticket = "\n".join([
            f"# Order: {intent['raw']}  ->  {rep['name']}  [{rep['best_feasibility']}]",
            "decompose: " + " -> ".join(rep["decomposition"]),
            "route to: " + ", ".join(makers),
            f"note: {rep.get('notes', '')}",
        ])
        return {"ticket": ticket, "steps": [], "machine_commands": [],
                "makers": makers, "feasibility": rep["best_feasibility"]}

    steps, cmds, makers = [], [], set()
    if intent["ice"]:
        steps.append(("watersynth", f"ICE ~{ICE_GRAMS} g", "freeze machine-made/treated water"))
        cmds.append(f"ICE {ICE_GRAMS}")
        makers.add("watersynth")
    if intent["chilled"]:
        steps.append(("watersynth", "CHILL glass", "Peltier plate below 5 C"))
        makers.add("watersynth")
    for ing, ml in intent["pour"].items():
        steps.append(("drinksynth", f"POUR {ing} {ml} mL", "peristaltic pump"))
        cmds.append(f"PUMP {ing} {ml}")
        makers.add("drinksynth")
    if intent["garnish"]:
        steps.append(("garnish/manual", f"GARNISH {intent['garnish']}", ""))
    steps.append(("serve", "SERVE", ""))
    cmds.append("DONE")

    lines = [f"# Order: {intent['raw']}  ->  {intent['name']}"]
    if intent.get("modifiers"):
        lines.append("modifiers: " + ", ".join(intent["modifiers"]))
    lines.append("build:")
    for ing, ml in intent["pour"].items():
        lines.append(f"  - {ing}: {ml} mL")
    if intent["ice"]:
        lines.append(f"  - ice (~{ICE_GRAMS} g, machine-made)")
    if intent["garnish"]:
        lines.append(f"  - garnish: {intent['garnish']}")
    lines.append("> assembles from stocked spirits/mixers + machine-made ice; "
                 "does not synthesise alcohol.")
    return {"ticket": "\n".join(lines),
            "steps": [{"maker": m, "action": a, "detail": d} for m, a, d in steps],
            "machine_commands": cmds, "makers": sorted(makers), "feasibility": "ready"}


def order(text, llm=None):
    """End-to-end: free-form text -> fulfillment plan."""
    return fulfill(interpret(text, llm=llm))
