"""
Drink recipes + the machine's ingredient<->pump map.

A recipe is a dict of ingredient -> millilitres, a target temperature, and an `iced`
flag. The machine dispenses each ingredient with a peristaltic pump, heats/chills the
cup with a Peltier, and (optionally) drops ice. This is ASSEMBLY FROM STOCKED
INGREDIENTS — not atomic synthesis. See ../../docs/vision.md for the honest scope.
"""

from __future__ import annotations

# Which pump dispenses which ingredient, and its calibrated flow rate (mL/s).
# Flow rate is per-pump; calibrate yours by timing a known volume.
PUMPS = {
    "water":      {"pump": 0, "ml_per_s": 2.2},
    "coffee":     {"pump": 1, "ml_per_s": 2.0},   # espresso / coffee concentrate
    "oat_milk":   {"pump": 2, "ml_per_s": 1.8},   # also used for soy/almond
    "dairy_milk": {"pump": 3, "ml_per_s": 1.8},
    "syrup":      {"pump": 4, "ml_per_s": 1.2},   # sweetener / flavour
}

HOT_C = 65       # default "hot" serving temperature
WARM_C = 50
ICED_C = 4       # chill plate target for iced drinks
BOIL_C = 90

# base drink -> (ingredients mL, target_c, iced)
RECIPES = {
    "espresso":   ({"coffee": 30}, HOT_C, False),
    "americano":  ({"coffee": 30, "water": 120}, HOT_C, False),
    "coffee":     ({"coffee": 30, "water": 180}, HOT_C, False),
    "latte":      ({"coffee": 30, "dairy_milk": 180}, 60, False),
    "oat latte":  ({"coffee": 30, "oat_milk": 180}, 60, False),
    "cappuccino": ({"coffee": 30, "dairy_milk": 120}, 62, False),
    "iced coffee": ({"coffee": 60, "water": 120}, ICED_C, True),
    "iced latte": ({"coffee": 60, "oat_milk": 150}, ICED_C, True),
    "cold brew":  ({"coffee": 80, "water": 170}, ICED_C, True),
    "hot water":  ({"water": 250}, BOIL_C, False),
    "iced water": ({"water": 250}, ICED_C, True),
}

DEFAULT_BASE = "coffee"
