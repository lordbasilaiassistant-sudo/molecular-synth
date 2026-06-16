"""
Request compiler:  "iced oat latte, large, extra shot"  ->  machine command sequence.

Same pattern as the molecular compiler (request -> compiler -> deterministic machine
recipe), at macroscale with cheap parts. Parsing is keyword-based and intentionally
simple/transparent (no black box): it resolves a base recipe, applies modifiers
(temperature, milk, size, extra shot, sweetener), then converts millilitres to per-pump
run-times and emits both a machine command list and a human-readable ticket.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import recipes as R


@dataclass
class Drink:
    request: str
    base: str
    ingredients: dict          # ingredient -> mL
    target_c: int
    iced: bool
    size_ml: float
    notes: list = field(default_factory=list)


def _match_base(text):
    # longest matching recipe name wins (so "iced latte" beats "latte")
    hits = [name for name in R.RECIPES if name in text]
    if not hits:
        # build a base from keywords
        if "latte" in text:
            return "oat latte" if ("oat" in text or "soy" in text or "almond" in text) else "latte"
        if "americano" in text:
            return "americano"
        if "espresso" in text or "shot" in text:
            return "espresso"
        if "water" in text:
            return "hot water"
        return R.DEFAULT_BASE
    return max(hits, key=len)


def parse(request: str) -> Drink:
    t = request.lower().strip()
    base = _match_base(t)
    ingredients, target_c, iced = R.RECIPES[base]
    ingredients = dict(ingredients)
    notes = []

    # temperature overrides
    if any(w in t for w in ("iced", "cold", "over ice", "chilled")):
        iced, target_c = True, R.ICED_C
    elif "warm" in t:
        iced, target_c = False, R.WARM_C
    elif "hot" in t and not iced:
        target_c = R.HOT_C
    if "extra hot" in t:
        target_c = min(R.BOIL_C, target_c + 10)

    # milk substitution
    if ("oat" in t or "soy" in t or "almond" in t) and "dairy_milk" in ingredients:
        ingredients["oat_milk"] = ingredients.pop("dairy_milk")
        notes.append("plant milk (oat channel)")
    if any(w in t for w in ("whole milk", "dairy", "regular milk")) and "oat_milk" in ingredients:
        ingredients["dairy_milk"] = ingredients.pop("oat_milk")

    # extra shot / double
    shots = t.count("extra shot") + (1 if "double" in t else 0)
    if "triple" in t:
        shots += 2
    if shots:
        ingredients["coffee"] = ingredients.get("coffee", 0) + 30 * shots
        notes.append(f"+{shots} shot(s)")

    # sweetener
    if any(w in t for w in ("sweet", "sugar", "syrup", "vanilla", "caramel")):
        ingredients["syrup"] = ingredients.get("syrup", 0) + 15
        notes.append("sweetened")

    # size scaling
    scale = 1.0
    if "large" in t or "venti" in t:
        scale = 1.4
    elif "small" in t:
        scale = 0.7
    if scale != 1.0:
        ingredients = {k: round(v * scale, 1) for k, v in ingredients.items()}
        notes.append(f"size x{scale}")

    if iced:
        notes.append("served over ice")

    size_ml = round(sum(ingredients.values()), 1)
    return Drink(request, base, ingredients, target_c, iced, size_ml, notes)


def compile_drink(request: str) -> dict:
    """Return {drink, commands, protocol}. `commands` is the serial protocol the
    firmware runs; `protocol` is the human ticket."""
    d = parse(request)
    commands = []
    # 1) thermal target up front so the cup is heating/chilling while pumping
    commands.append(f"TEMP {d.target_c}")
    if d.iced:
        commands.append("ICE 40")          # ~40 g ice (optional ice dropper)
    # 2) dispense each ingredient (mL -> pump run-time ms)
    total_s = 0.0
    for ing, ml in d.ingredients.items():
        spec = R.PUMPS.get(ing)
        if not spec or ml <= 0:
            continue
        ms = int(round(ml / spec["ml_per_s"] * 1000))
        commands.append(f"PUMP {spec['pump']} {ms}   ; {ing} {ml} mL")
        total_s += ms / 1000.0
    # 3) hold to reach serving temperature, then signal ready
    commands.append("WAIT_TEMP")
    commands.append("DONE")

    lines = [
        f"# Ticket: {d.request}",
        f"Base: {d.base}    Size: {d.size_ml} mL    Serve: "
        f"{'ICED ~' + str(d.target_c) if d.iced else str(d.target_c)} C",
        "Build:",
    ]
    for ing, ml in d.ingredients.items():
        lines.append(f"  - {ing.replace('_', ' ')}: {ml} mL")
    if d.notes:
        lines.append("Notes: " + ", ".join(d.notes))
    lines.append(f"Est. dispense time: {total_s:.0f}s (+ heat/chill)")
    lines.append("")
    lines.append("> Assembly from stocked ingredients - not atomic synthesis "
                 "(see docs/vision.md).")

    return {"drink": d, "commands": commands, "protocol": "\n".join(lines)}
