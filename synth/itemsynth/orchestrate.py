"""
The unified front door — one entry point over every federation engine.

itemsynth is THE front door of the maker federation (docs/vision.md, README). router.py
dispatches a request to a single maker; this module widens that into the full surface the
thesis promises by delegating to the **Maker Catalog** (catalog/makerlib) for the two jobs
the single-maker router can't do alone:

    route(request)        -> run the one maker that fits           (router.py)
    feasibility(request)  -> "can the system make X, on which rung?" (catalog report)
    plan(request)         -> cross-maker fulfillment plan            (catalog order brain)
    synthesize(request)   -> smart front door: dispatch a maker if one fits, else fall back
                             to plan() so cataloged / multi-maker asks still resolve

The catalog is thereby an *engine of the one front door*, not a second disconnected front
door — the federation has a single spine. The catalog packages are imported lazily through
the shared `ensure_federation_paths()` seam, so engines that don't need them cost nothing.
"""
from __future__ import annotations

from .makers import ensure_federation_paths, MAKER_DOMAINS
from .router import route, classify


def feasibility(request: str) -> dict:
    """Feasibility report for `request` via the Maker Catalog: which rung of the ladder it
    sits on (ready / assemble / frontier / north-star), which maker, and how it decomposes
    to atoms. Delegates to catalog/makerlib so there is one front door, not two."""
    ensure_federation_paths()
    from makerlib.checker import check
    return check(request)


def plan(request: str) -> dict:
    """Cross-maker fulfillment plan for `request` — decomposes orders like 'whiskey on the
    rocks' into ice (watersynth) + pour (drinksynth) across makers, or falls through to a
    catalog feasibility report for non-drinks. Delegates to the catalog order brain."""
    ensure_federation_paths()
    from makerlib.order import order
    return order(request)


def synthesize(request: str, outdir: str = None, compile_molecular: bool = True) -> dict:
    """The one-call front door. If a single maker clearly fits the request, run it (route);
    for the honestly-impossible, return the north-star verdict; otherwise fall back to the
    catalog plan so multi-maker and cataloged asks ('whiskey on the rocks', 'a cookie')
    resolve through a real engine instead of dead-ending at 'unknown'.

    Returns the route() result dict for maker/north-star hits; for catalog fallbacks a dict
    with the same {request, maker, recipe, ticket, honest_note} keys plus `makers` (the
    cross-maker list) and `feasibility` (the rung), and `domain="catalog"`."""
    c = classify(request)
    if c["domain"] in MAKER_DOMAINS or c["domain"] == "north-star":
        return route(request, outdir=outdir, compile_molecular=compile_molecular)

    # Unknown to the single-maker classifier -> let the catalog decompose / report it.
    p = plan(request)
    return {
        "request": request, "domain": "catalog", "maker": None,
        "makers": p.get("makers", []),
        "recipe": p.get("machine_commands") or None,
        "ticket": p["ticket"],
        "feasibility": p.get("feasibility"),
        "honest_note": "resolved via the Maker Catalog (cross-maker decomposition / feasibility)",
    }
