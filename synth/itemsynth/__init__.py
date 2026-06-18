"""
Item Synth — the AI request-compiler that fronts the whole maker federation.

This is the embodiment of the synthesizer thesis (docs/vision.md): *ask for X, and the
right cheap desktop maker makes it.* You give one natural request; a transparent classifier
routes it to the maker whose domain fits (Water / Drink / Print / Molecular nanostructure)
and returns that maker's machine recipe. Requests that no desktop maker can honestly satisfy
today (working electronics, arbitrary macroscopic matter from atoms) are NOT faked -- they
return the honest north-star verdict (docs/north-star.md), matching the project rule of
never overclaiming a rung we can't stand on.

    from itemsynth import route
    r = route("a large glass of cold water")
    print(r["maker"], "->", r["recipe"])         # 'water' -> serial command list

The classifier is a deterministic, inspectable keyword scorer (no LLM, no black box), so
every routing decision is reproducible and explains itself (`r["matched"]`).

CLI:  python -m itemsynth "iced oat latte, large"
"""
from .router import route, classify          # noqa: F401
from .makers import MAKERS, MAKER_DOMAINS, Maker   # noqa: F401

__version__ = "0.1.0"
