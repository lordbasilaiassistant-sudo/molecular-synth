"""
Rung 2 of the ladder (docs/the-ladder.md): DNA as a BREADBOARD.

Extend chosen staples with single-stranded "handle" sequences that protrude from the
folded structure at known coordinates. A guest (enzyme, catalyst, nanoparticle, dye)
carrying the complementary "anti-handle" hybridises to the handle and is positioned with
nm precision - the demonstrated route from "make a shape" to "make a shape that does
chemistry."

Demonstrations:
  * Fu, J. et al. "Multienzyme complexes on a DNA scaffold..." J. Am. Chem. Soc. 134,
    5516 (2012) - enzyme cascades positioned on origami via handles.
  * Kuzyk, A. et al. "DNA-based self-assembly of chiral plasmonic nanostructures..."
    Nature 483, 311 (2012) - nanoparticles placed at handle sites.

HONEST SCOPE: handles POSITION a guest you attach; they do not synthesise it. This is
standard, demonstrated origami functionalisation - the first chemistry-capable rung.
"""

from __future__ import annotations

import random

from . import sequences as sq

HANDLE_LEN = 20
DEFAULT_SPACER = "TT"
_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _lcs_len(a, b):
    """Longest common substring length (for cross-hybridisation screening)."""
    n = len(b)
    prev = [0] * (n + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (n + 1)
        ai = a[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def _orthogonal(h, chosen, scaffold, max_cross=7):
    rc = sq.reverse_complement(h)
    if h in scaffold or rc in scaffold:      # must not bind the scaffold (either way)
        return False
    for g in chosen:                          # must not cross-bind another handle
        if _lcs_len(rc, g) >= max_cross or _lcs_len(sq.reverse_complement(g), h) >= max_cross:
            return False
    return True


def generate_handles(scaffold, n=24, length=HANDLE_LEN, seed=20240601):
    """A set of mutually orthogonal handle sequences absent from the scaffold:
    balanced GC, no long runs, no hairpin, low pairwise cross-hybridisation."""
    rng = random.Random(seed)
    bases = "ACGT"
    chosen = []
    tries = 0
    while len(chosen) < n and tries < 500000:
        tries += 1
        h = "".join(rng.choice(bases) for _ in range(length))
        if not (0.40 <= sq.gc_content(h) <= 0.60):
            continue
        if sq.max_homopolymer_run(h) > 3:
            continue
        if sq.hairpin_score(h) > 0:
            continue
        if not _orthogonal(h, chosen, scaffold):
            continue
        chosen.append(h)
    return chosen


def _staple_edge(staple, routing):
    mid = (staple.scaffold_start + staple.scaffold_end) // 2
    for seg in routing.segments:
        if seg.scaffold_start <= mid < seg.scaffold_start + seg.bp:
            return seg.edge
    return None


def decorate(staples, routing, n, end="3p", spacer=DEFAULT_SPACER, guests=None):
    """Attach n orthogonal handles to staples spread across the structure (preferring
    crossover staples = well-defined vertex positions). Mutates the chosen staples
    (sets .handle/.handle_end/.spacer/.guest) and returns the decoration records."""
    handles = generate_handles(routing.scaffold_seq, n=max(n, 1))
    n = min(n, len(handles))
    cands = [s for s in staples if s.crossovers > 0] or list(staples)
    cands = sorted(cands, key=lambda s: s.scaffold_start)
    picks = [cands[int(i * len(cands) / n)] for i in range(n)] if n else []
    guests = guests or []

    records = []
    for i, s in enumerate(picks):
        s.handle = handles[i]
        s.handle_end = end
        s.spacer = spacer
        s.guest = guests[i] if i < len(guests) else f"guest_{_LABELS[i % 26]}"
        records.append({
            "label": _LABELS[i % 26],
            "staple": s.name,
            "well": s.well,
            "edge": _staple_edge(s, routing),
            "scaffold_pos": [s.scaffold_start, s.scaffold_end],
            "guest": s.guest,
            "handle": s.handle,
            "anti_handle": sq.reverse_complement(s.handle),
            "end": end,
            "spacer": spacer,
        })
    return records


def decoration_md(design_name, records):
    if not records:
        return ""
    rows = "\n".join(
        f"| {r['label']} | {r['guest']} | {r['staple']} ({r['well']}) | "
        f"edge {r['edge']} | {r['end']} | `{r['handle']}` | `{r['anti_handle']}` |"
        for r in records)
    return f"""# Decoration map (DNA breadboard) - {design_name}

Rung 2 of the ladder: each handle below protrudes from the folded origami at a known
site. Attach your guest (enzyme / catalyst / nanoparticle / dye) by conjugating it to the
**anti-handle** (the reverse complement); it then hybridises to the handle and is
positioned at that site. Order the decorated staples as their full `order_sequence`
(staple + {records[0]['spacer']} spacer + handle, on the {records[0]['end']} end) - see
staples.csv.

| Site | Guest | Staple (well) | Location | End | Handle (on origami, 5'->3') | Anti-handle (on guest, 5'->3') |
|------|-------|---------------|----------|-----|------------------------------|--------------------------------|
{rows}

**How to attach a guest:**
1. Conjugate the **anti-handle** oligo to your guest (NHS-ester/thiol/click for proteins;
   thiol-DNA for Au nanoparticles; or buy the guest pre-modified).
2. After folding + purifying the origami, add the guest-anti-handle in modest excess.
3. Incubate (RT, in the Mg2+ buffer); it hybridises to its handle at the mapped site.
4. Verify placement by gel shift / AFM / TEM (handles add mass at known positions).

> Honest scope: handles POSITION a guest you supply; they do not synthesise it. This is
> demonstrated origami functionalisation (Fu et al. 2012; Kuzyk et al. 2012) - the first
> chemistry-capable rung of docs/the-ladder.md.
"""
