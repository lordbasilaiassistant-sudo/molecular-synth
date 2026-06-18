"""
The maker registry — the federation's single source of truth.

Each `Maker` bundles three things that used to be scattered across router.py:
  1. its `domain` name,
  2. the weighted `keywords` table that votes for it during classification, and
  3. a `run` adapter that calls that maker's native compiler and normalizes the
     heterogeneous output into the uniform router result ({recipe, ticket, honest_note,
     ...}).

The router (router.py) is generic over `MAKERS`: to add a maker you add one entry here and
classify()/route() need no changes. The maker compilers live in synth/<name> (water / drink
/ print) and compiler/molsynth (molecular); each is imported lazily inside its run() so an
unused maker costs no imports. Pure stdlib otherwise.
"""
from __future__ import annotations

import os
import re
import sys
import tempfile
from dataclasses import dataclass
from typing import Callable

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

# --------------------------------------------------------------------------- #
# Import-path bootstrap + molecular target resolution (maker-specific helpers).
# --------------------------------------------------------------------------- #
_SHAPES = ("tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron",
           "square", "dodec")


def _ensure_paths() -> None:
    """Put synth/ and compiler/ on sys.path so the maker packages import, regardless of
    where the caller runs from."""
    here = os.path.dirname(os.path.abspath(__file__))           # synth/itemsynth
    synth_dir = os.path.dirname(here)                           # synth/
    repo = os.path.dirname(synth_dir)                           # repo root
    for p in (synth_dir, os.path.join(repo, "compiler")):
        if p not in sys.path:
            sys.path.insert(0, p)


def _extract_stl_path(request: str):
    """If the request names an existing .stl/.obj file, return its path (for exact print
    metrics); else None (fall back to a nominal estimate)."""
    for tok in re.findall(r"\S+\.(?:stl|obj)\b", request, flags=re.IGNORECASE):
        if os.path.exists(tok):
            return tok
    return None


def _pick_shape(request: str) -> str:
    """Resolve the molecular target: a named mesh FILE (.stl/.ply/.json) if the request
    points at one (compile_shape reads those directly), else a named Platonic preset, else
    the smallest preset as a fast default."""
    for tok in re.findall(r"\S+\.(?:stl|ply|json)\b", request, flags=re.IGNORECASE):
        if os.path.exists(tok):
            return tok
    text = request.lower()
    for s in _SHAPES:
        if s in text:
            return "dodecahedron" if s == "dodec" else s
    return "tetrahedron"          # smallest, fastest default when no shape is named


# --------------------------------------------------------------------------- #
# Run adapters: call each maker's native compiler, return the uniform result fields.
# Unused router options are accepted and ignored via **_ so the registry stays generic.
# --------------------------------------------------------------------------- #
def _run_water(request: str, **_) -> dict:
    _ensure_paths()
    from watersynth import compile_water
    out = compile_water(request)
    return {"maker": "water", "recipe": out["commands"], "ticket": out["protocol"],
            "honest_note": "harvested+treated from air, not synthesised"}


def _run_drink(request: str, **_) -> dict:
    _ensure_paths()
    from drinksynth import compile_drink
    out = compile_drink(request)
    return {"maker": "drink", "recipe": out["commands"], "ticket": out["protocol"],
            "honest_note": "assembled from stocked ingredients"}


def _run_print(request: str, **_) -> dict:
    _ensure_paths()
    from printsynth import compile_print
    stl = _extract_stl_path(request)
    if stl:
        # real geometry -> exact material/time/cost from the mesh
        job = compile_print(stl=stl)
        note = f"measured from {os.path.basename(stl)}"
    else:
        # no STL in a text request -> estimate from a nominal small part so the user still
        # gets a real material/time/cost ballpark.
        job = compile_print(volume_cm3=10.0, bbox_mm=(40, 40, 25), name=request[:40])
        note = "estimate from a nominal 10 cm^3 part; supply an .stl for exact numbers"
    return {"maker": "print", "recipe": job["commands"], "ticket": job["protocol"],
            "honest_note": note}


def _run_molecular(request: str, outdir: str = None, compile_molecular: bool = True, **_) -> dict:
    shape = _pick_shape(request)
    if not compile_molecular:
        return {"maker": "molecular", "recipe": None, "shape": shape,
                "ticket": f"would compile a DNA-origami {shape} (scaffold + staples + 3D + protocol)",
                "honest_note": "classify-only; set compile_molecular=True to emit the design"}
    _ensure_paths()
    from molsynth import compile_shape
    od = outdir or tempfile.mkdtemp(prefix="itemsynth_")
    summary = compile_shape(shape, outdir=od)
    return {"maker": "molecular", "shape": shape, "outdir": od,
            "recipe": ["ORDER staples.csv", "FOLD per protocol.md", "VERIFY gel band"],
            "ticket": f"DNA-origami {shape} compiled to {od} (scaffold.fasta, staples.csv, "
                      f"protocol.md, 3D oxDNA/PDB, diagnostics.md)",
            "summary": summary,
            "honest_note": "DNA self-assembled nanostructure (~10nm-1um), not macroscopic"}


@dataclass(frozen=True)
class Maker:
    """One maker in the federation: a domain name, its keyword voting table, and the
    adapter that runs its compiler and yields the uniform router result fields."""
    domain: str
    keywords: list
    run: Callable[..., dict]


# The registry. Order matters only for tie-breaking in classify() (stable sort keeps this
# order), preserving the historical water > drink > print > molecular precedence.
MAKERS = (
    Maker("water", _WATER, _run_water),
    Maker("drink", _DRINK, _run_drink),
    Maker("print", _PRINT, _run_print),
    Maker("molecular", _NANO, _run_molecular),
)

MAKER_DOMAINS = tuple(m.domain for m in MAKERS)
BY_DOMAIN = {m.domain: m for m in MAKERS}
