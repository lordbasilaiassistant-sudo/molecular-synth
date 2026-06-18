"""
Request router for the maker federation — the thin, generic front door.

`classify(request)` scores the request against every maker's keyword table (declared in
makers.py) plus the impossible-today table, and returns the best domain (plus the matched
terms and the runner-up, so the decision is auditable). `route(request)` dispatches that
domain to its maker via the registry adapter and returns a uniform result dict.
Impossible-today requests resolve to the honest north-star verdict instead of a fabricated
recipe.

All maker-specific knowledge (keywords, how to call each compiler, how to normalize its
output) lives in makers.py; this module is generic over the `MAKERS` registry, so adding a
maker never touches the classify/route logic. Pure stdlib — makers are imported lazily.
"""
from __future__ import annotations

import re

from .makers import MAKERS, MAKER_DOMAINS, BY_DOMAIN   # noqa: F401  (MAKER_DOMAINS re-exported)

# Impossible-today: macroscopic functional electronics, or true atom-up matter replication.
# These are NOT a maker -- they're the federation's honest refusal, so the table lives here
# (next to the north-star verdict) rather than in the registry. Crafted to avoid bare nouns
# that legitimately route elsewhere (e.g. "phone case" -> print).
_IMPOSSIBLE = [
    (r"\bsmartphone\b", 5), (r"\bworking phone\b", 5), (r"\bcell ?phone\b(?! case)", 4),
    (r"\blaptop\b", 5), (r"\bcomputer\b", 4), (r"\bcpu\b", 5), (r"\bgpu\b", 5),
    (r"\bmicrochip\b", 5), (r"\bsemiconductor\b", 5), (r"\bintegrated circuit\b", 5),
    (r"\bbattery\b", 4), (r"\bprocessor\b", 4), (r"\bfrom atoms\b", 6),
    (r"\bfrom energy\b", 6), (r"\bmatter replicat\w*\b", 6), (r"\breplicate matter\b", 6),
    (r"\bstar[- ]?trek replicator\b", 6), (r"\barbitrary (matter|object)\b", 6),
    (r"\bany(thing| object) (you want|at all)\b", 4), (r"\bout of thin air\b", 4),
    (r"\bgold\b", 3), (r"\bdiamond(oid)?\b", 3), (r"\bsteak\b", 3), (r"\bmeal\b", 3),
    (r"\bfood\b", 3),
]


def _label(pat: str) -> str:
    """A clean, human-readable name for a keyword pattern (strip regex syntax)."""
    s = re.sub(r"\\b|\(\?![^)]*\)|[\\()?]", "", pat)   # drop \b, lookaheads, regex chars
    s = s.replace("w*", "").replace("|", "/").replace("[- ]", " ")
    return re.sub(r"\s+", " ", s).strip()


def _score(request: str, table):
    """Total weight of matched patterns + the human-readable terms that matched."""
    text = request.lower()
    total, hits = 0, []
    for pat, w in table:
        if re.search(pat, text):
            total += w
            hits.append(_label(pat))
    return total, hits


def classify(request: str) -> dict:
    """Route `request` to a domain. Returns a dict with the chosen `domain`
    ('water'|'drink'|'print'|'molecular'|'north-star'|'unknown'), the numeric `confidence`
    (winning score), the `matched` terms that drove it, and the `runner_up` (domain, score)
    so the decision is fully auditable. 'north-star' = honestly impossible today; 'unknown'
    = nothing matched (caller should ask the user to be more specific)."""
    scores = {m.domain: _score(request, m.keywords) for m in MAKERS}
    imp_score, imp_hits = _score(request, _IMPOSSIBLE)

    # stable sort keeps registry order on ties (water > drink > print > molecular)
    ranked = sorted(scores.items(), key=lambda kv: kv[1][0], reverse=True)
    (best_dom, (best_score, best_hits)) = ranked[0]
    (run_dom, (run_score, _)) = ranked[1]

    # A buildable maker wins ties against the impossible bucket (so "phone case" -> print,
    # "a glass of water" -> water); the north-star verdict only fires when nothing
    # buildable matches as strongly as the impossible signal.
    if imp_score > best_score:
        return {"domain": "north-star", "confidence": imp_score, "matched": imp_hits,
                "runner_up": (best_dom, best_score) if best_score else None}
    if best_score == 0:
        return {"domain": "unknown", "confidence": 0, "matched": [], "runner_up": None}
    return {"domain": best_dom, "confidence": best_score, "matched": best_hits,
            "runner_up": (run_dom, run_score) if run_score else None}


# --------------------------------------------------------------------------- #
# Dispatch
# --------------------------------------------------------------------------- #
_NORTH_STAR = (
    "No cheap desktop maker can honestly do this today. A working device needs "
    "semiconductor fabs + multi-material assembly; arbitrary matter from atoms needs "
    "positional mechanosynthesis, which has never been demonstrated (simulation only). "
    "This is the project's north star, not a buildable rung. See docs/north-star.md and "
    "docs/vision.md -- we never fake a recipe for a rung we can't stand on."
)


def route(request: str, outdir: str = None, compile_molecular: bool = True) -> dict:
    """Classify `request` and dispatch to the matching maker. Returns a uniform dict:
        {request, domain, confidence, matched, runner_up, maker, recipe, ticket, honest_note}
    For 'north-star' / 'unknown' there is no maker; `recipe`/`ticket` carry the honest
    explanation. The molecular maker writes design files to `outdir` (a temp dir if None)
    and is imported lazily so the other domains need nothing beyond stdlib. Set
    compile_molecular=False to classify-only for nanostructures (skip the heavy compile)."""
    c = classify(request)
    dom = c["domain"]
    base = {"request": request, "domain": dom, "confidence": c["confidence"],
            "matched": c["matched"], "runner_up": c.get("runner_up")}

    if dom == "north-star":
        return {**base, "maker": None, "recipe": None, "ticket": _NORTH_STAR,
                "honest_note": "impossible-today; routed to north-star, not faked"}
    if dom == "unknown":
        return {**base, "maker": None, "recipe": None,
                "ticket": ("Couldn't tell which maker this needs. Try naming a drink "
                           "(coffee/tea), water, a printable object (case/bracket/.stl), "
                           "or a nanostructure (tetrahedron/octahedron/DNA cage)."),
                "honest_note": "no domain matched; ask the user to be specific"}

    result = BY_DOMAIN[dom].run(request, outdir=outdir, compile_molecular=compile_molecular)
    return {**base, **result}
