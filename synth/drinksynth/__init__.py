"""
Drink Synth — the buildable-today instance of the synthesizer thesis.

    from drinksynth import compile_drink
    out = compile_drink("iced oat latte, large, extra shot")
    print(out["protocol"]); print("\n".join(out["commands"]))

CLI:  python -m drinksynth make "hot americano"   [--port COM4 | --dry-run]

Honest scope: assembles a drink from stocked ingredients with cheap pumps + a Peltier
hot/cold plate. It does not synthesise matter. See ../docs/vision.md.
"""
from .compiler import compile_drink, parse, Drink   # noqa: F401

__version__ = "0.1.0"
