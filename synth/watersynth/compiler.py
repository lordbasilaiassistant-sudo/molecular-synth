"""
Water request compiler:  "large glass of cold water" -> machine command sequence.

Same pattern as drinksynth / molsynth (request -> compiler -> deterministic machine
recipe). Resolves a temperature + volume, then emits: harvest-from-air (or reservoir),
filter, UV-sterilise, set temperature, dispense.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import recipes as R


@dataclass
class WaterOrder:
    request: str
    temp_c: int
    volume_ml: int
    notes: list


def parse(request: str) -> WaterOrder:
    t = request.lower().strip()
    base = R.DEFAULT
    # longest preset name match wins ("cold water" beats "water")
    hits = [name for name in R.PRESETS if name in t]
    if hits:
        base = max(hits, key=len)
    elif "cold" in t or "chilled" in t or "ice" in t:
        base = "ice water" if "ice" in t else "cold water"
    elif "hot" in t or "boiling" in t:
        base = "hot water"
    elif "warm" in t:
        base = "warm water"
    temp_c, vol = R.PRESETS[base]

    notes = []
    if "large" in t or "big" in t:
        vol = int(vol * 1.6); notes.append("large")
    elif "small" in t:
        vol = int(vol * 0.6); notes.append("small")
    return WaterOrder(request, temp_c, vol, notes)


def compile_water(request: str, from_reservoir: bool = False) -> dict:
    """Return {order, commands, protocol}. from_reservoir=True skips the air-harvest
    step (use a pre-filled tank instead of condensing from air)."""
    o = parse(request)
    cmds = []
    harvest_min = o.volume_ml / R.HARVEST_ML_PER_MIN
    if not from_reservoir:
        cmds.append(f"HARVEST {o.volume_ml}    ; condense ~{o.volume_ml} mL from air "
                    f"(~{harvest_min:.0f} min, humidity-dependent)")
    cmds.append("FILTER            ; activated-carbon inline (passive)")
    uv_s = int(math.ceil(o.volume_ml / 100 * R.UV_SECONDS_PER_100ML))
    cmds.append(f"UV {uv_s}             ; UV-C sterilise")
    cmds.append(f"TEMP {o.temp_c}           ; serving temperature")
    cmds.append(f"DISPENSE {o.volume_ml}  ; pour to cup")
    cmds.append("DONE")

    lines = [
        f"# Ticket: {o.request}",
        f"Water: {o.volume_ml} mL @ {o.temp_c} C"
        + (f"   ({', '.join(o.notes)})" if o.notes else ""),
        f"Source: {'reservoir' if from_reservoir else 'harvested from air (AWG)'}"
        f" -> carbon filter -> UV-C -> temperature -> cup",
        "",
        "> Harvested + treated from air/reservoir, NOT synthesised from energy "
        "(see docs/vision.md). This is the buildable-today 'glass of water on demand'.",
    ]
    return {"order": o, "commands": cmds, "protocol": "\n".join(lines)}
