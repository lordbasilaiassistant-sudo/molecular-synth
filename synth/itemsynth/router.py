"""
Request router for the maker federation.

`classify(request)` scores the request against each maker domain with a transparent,
weighted keyword table and returns the best domain (plus the matched terms and the
runner-up, so the decision is auditable). `route(request)` dispatches to that maker's
compiler and returns a uniform result dict. Impossible-today requests resolve to the
honest north-star verdict instead of a fabricated recipe.

Pure stdlib. The molecular maker lives in compiler/molsynth and is imported lazily only
when a request actually routes there, so water/drink/print need nothing extra.
"""
from __future__ import annotations

import os
import re
import sys

# --------------------------------------------------------------------------- #
# Domain keyword tables. Each (pattern, weight): word-boundary regex -> score.
# Weights let a specific term ("espresso") outrank a generic co-occurring one
# ("drink"), and let "glass of water" beat the bare "drink" sense.
# --------------------------------------------------------------------------- #
_WATER = [
    (r"\bwater\b", 3), (r"\bhydrat\w*\b", 2), (r"\bglass of water\b", 5),
    (r"\bdrinking water\b", 5), (r"\bh2o\b", 4), (r"\bthirsty\b", 2),
]
_DRINK = [
    (r"\bcoffee\b", 4), (r"\blatte\b", 5), (r"\bespresso\b", 5), (r"\bamericano\b", 5),
    (r"\bcappuccino\b", 5), (r"\bmocha\b", 5), (r"\btea\b", 4), (r"\bmatcha\b", 5),
    (r"\bjuice\b", 4), (r"\bcocktail\b", 4), (r"\bsmoothie\b", 4), (r"\bsoda\b", 3),
    (r"\bbrew\b", 2), (r"\bcaffeine\b", 3), (r"\bdrink\b", 2), (r"\biced\b", 2),
    (r"\bbeverage\b", 3),
]
_PRINT = [
    (r"\bprint\b", 3), (r"\b3d[- ]?print\w*\b", 5), (r"\.stl\b", 5), (r"\.obj\b", 4),
    (r"\bcase\b", 3), (r"\bbracket\b", 4), (r"\bmount\b", 3), (r"\bholder\b", 3),
    (r"\benclosure\b", 4), (r"\bclip\b", 3), (r"\bgear\b", 3), (r"\bknob\b", 3),
    (r"\bfigurine\b", 4), (r"\bminiature\b", 3), (r"\bwidget\b", 2), (r"\bpart\b", 2),
    (r"\bphone case\b", 6), (r"\bplastic\b", 2), (r"\bprusa\b", 3), (r"\bfilament\b", 3),
]
_NANO = [
    (r"\bnanostructure\b", 5), (r"\bnano\w*\b", 4), (r"\borigami\b", 4), (r"\bdna\b", 4),
    (r"\bscaffold\b", 3), (r"\bnanocage\b", 5), (r"\btetrahedron\b", 4), (r"\bcube\b", 3),
    (r"\boctahedron\b", 4), (r"\bicosahedron\b", 4), (r"\bdodecahedron\b", 4),
    (r"\bnanoparticle\b", 4), (r"\bwireframe\b", 3), (r"\bpolyhedron\b", 3),
    (r"\baptamer\b", 3), (r"\benzyme cage\b", 4), (r"\bself[- ]assembl\w*\b", 3),
]

# Impossible-today: macroscopic functional electronics, or true atom-up matter
# replication. These are NOT routed to a maker -- they get the honest north-star verdict.
# Crafted to avoid bare nouns that legitimately route elsewhere (e.g. "phone case" -> print).
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

MAKERS = ("water", "drink", "print", "molecular")


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
    scores = {
        "water": _score(request, _WATER),
        "drink": _score(request, _DRINK),
        "print": _score(request, _PRINT),
        "molecular": _score(request, _NANO),
    }
    imp_score, imp_hits = _score(request, _IMPOSSIBLE)

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

_SHAPES = ("tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron",
           "square", "dodec")


def _pick_shape(request: str) -> str:
    text = request.lower()
    for s in _SHAPES:
        if s in text:
            return "dodecahedron" if s == "dodec" else s
    return "tetrahedron"          # smallest, fastest default when no shape is named


def route(request: str, outdir: str = None, compile_molecular: bool = True) -> dict:
    """Classify `request` and dispatch to the matching maker. Returns a uniform dict:
        {request, domain, confidence, matched, maker, recipe, ticket, honest_note}
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

    # ensure the makers are importable (synth/ on path) and dispatch
    _ensure_paths()
    if dom == "water":
        from watersynth import compile_water
        out = compile_water(request)
        return {**base, "maker": "water", "recipe": out["commands"],
                "ticket": out["protocol"], "honest_note": "harvested+treated from air, not synthesised"}
    if dom == "drink":
        from drinksynth import compile_drink
        out = compile_drink(request)
        return {**base, "maker": "drink", "recipe": out["commands"],
                "ticket": out["protocol"], "honest_note": "assembled from stocked ingredients"}
    if dom == "print":
        from printsynth import compile_print
        # no STL in a text request -> estimate from a nominal small part so the user gets a
        # real material/time/cost ballpark; hand a real STL to printsynth for exact numbers.
        job = compile_print(volume_cm3=10.0, bbox_mm=(40, 40, 25), name=request[:40])
        return {**base, "maker": "print", "recipe": job["commands"],
                "ticket": job["protocol"],
                "honest_note": "estimate from a nominal 10 cm^3 part; supply an .stl for exact numbers"}
    if dom == "molecular":
        shape = _pick_shape(request)
        if not compile_molecular:
            return {**base, "maker": "molecular", "recipe": None, "shape": shape,
                    "ticket": f"would compile a DNA-origami {shape} (scaffold + staples + 3D + protocol)",
                    "honest_note": "classify-only; set compile_molecular=True to emit the design"}
        from molsynth import compile_shape
        import tempfile
        od = outdir or tempfile.mkdtemp(prefix="itemsynth_")
        summary = compile_shape(shape, outdir=od)
        return {**base, "maker": "molecular", "shape": shape, "outdir": od,
                "recipe": [f"ORDER staples.csv", f"FOLD per protocol.md", f"VERIFY gel band"],
                "ticket": f"DNA-origami {shape} compiled to {od} (scaffold.fasta, staples.csv, "
                          f"protocol.md, 3D oxDNA/PDB, diagnostics.md)",
                "summary": summary,
                "honest_note": "DNA self-assembled nanostructure (~10nm-1um), not macroscopic"}
    raise AssertionError(f"unhandled domain {dom!r}")


def _ensure_paths():
    """Put synth/ and compiler/ on sys.path so the maker packages import, regardless of
    where the caller runs from."""
    here = os.path.dirname(os.path.abspath(__file__))           # synth/itemsynth
    synth_dir = os.path.dirname(here)                           # synth/
    repo = os.path.dirname(synth_dir)                           # repo root
    for p in (synth_dir, os.path.join(repo, "compiler")):
        if p not in sys.path:
            sys.path.insert(0, p)
