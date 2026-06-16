"""
Water Synth — "a glass of drinkable water on demand", buildable today.

Harvests water from ambient air by Peltier condensation (atmospheric water generation),
filters + UV-treats it, sets temperature, and dispenses. Reuses the molecular rig's
Peltier. Honest scope: harvest + treat + dispense, NOT energy->matter synthesis.
See ../docs/vision.md.

    from watersynth import compile_water
    print(compile_water("large glass of cold water")["protocol"])

CLI:  python -m watersynth make "cold water"   [--reservoir | --port COM5]
"""
from .compiler import compile_water, parse, WaterOrder   # noqa: F401

__version__ = "0.1.0"
