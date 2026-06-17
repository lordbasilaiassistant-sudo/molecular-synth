"""
Scaffold sourcing + routing.

1. Scaffold sequence: the long single strand that threads the whole structure.
   The canonical origami scaffold is the M13mp18 phage genome (7249 nt), sold as
   ssDNA by NEB / tilibit / Guild Biosciences (see bom/). `load_scaffold()` reads
   data/m13mp18.txt if present, otherwise emits a clearly-labelled *deterministic
   synthetic* scaffold so the compiler always runs end-to-end offline. Run
   `python -m molsynth fetch-scaffold` to pull the real M13mp18 sequence.

2. Routing: reduce the wireframe Mesh to a single closed scaffold walk that
   traverses every edge exactly twice (once in each direction) -- an Eulerian circuit
   of the doubled directed edge multigraph (Hierholzer's algorithm). Every vertex of
   that multigraph is in/out balanced, so a circuit always exists for any CONNECTED
   mesh. The traversal is BIASED by the face rotation system (the A-trail "turn to the
   next edge" rule) so the scaffold traces faces and avoids vertex crossings, while
   Hierholzer still guarantees a single closed scaffold - i.e. face-aware A-trail-style
   routing (Benson et al., Nature 523:441, 2015; Veneziano et al., Science 352:1534,
   2016). The rotation bias is a preference, not a hard guarantee of a perfect A-trail;
   meshes without faces fall back to an arbitrary single Eulerian circuit.

   HONEST SCOPE: this produces a *topologically valid, sequence-valid* routing
   (single scaffold loop covering all edges exactly twice; staples are exact reverse
   complements so they really hybridize). Edge lengths are geometrically scaled and
   snapped to integer helical turns (BP_PER_TURN), but the routing does NOT compute
   production 3D crossover geometry / in-phase crossovers / helix packing. For
   fabrication-grade designs, export to scadnano/caDNAno/PERDIX (see export.py) and
   relax in oxDNA. See docs/science.md. Disconnected meshes are rejected (a single
   scaffold cannot thread separate components).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

BP_PER_TURN = 10.5
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
M13_PATH = os.path.join(DATA_DIR, "m13mp18.txt")
M13_LEN = 7249


@dataclass
class Segment:
    """One traversal of one edge by the scaffold."""
    order: int                # position in the scaffold walk
    arc: tuple                # directed (u, v)
    edge: tuple               # undirected (min, max)
    bp: int                   # length in base pairs
    scaffold_start: int       # index into the scaffold sequence
    seq: str                  # scaffold bases for this segment (5'->3')


@dataclass
class Routing:
    scaffold_name: str
    scaffold_len_used: int
    scaffold_seq: str         # the concatenated scaffold route, 5'->3'
    segments: list            # list[Segment]
    edge_bp: dict             # undirected edge -> bp length
    crossover_positions: list # scaffold indices that are vertex/crossover boundaries
    synthetic: bool


# --------------------------------------------------------------------------- #
# Scaffold sequence
# --------------------------------------------------------------------------- #
def _synthetic_scaffold(length: int = M13_LEN, seed: int = 7249) -> str:
    """Deterministic pseudo-random ACGT scaffold (LCG, no `random` import) so the
    end-to-end path is reproducible and offline. NOT for wet-lab use."""
    bases = "ACGT"
    out = []
    x = seed
    for _ in range(length):
        x = (1103515245 * x + 12345) & 0x7FFFFFFF
        out.append(bases[(x >> 16) & 3])
    return "".join(out)


def load_scaffold():
    """Return (sequence, name, synthetic_flag)."""
    if os.path.exists(M13_PATH):
        with open(M13_PATH, "r", encoding="utf-8") as fh:
            raw = fh.read()
        seq = "".join(c for c in raw.upper() if c in "ACGT")
        if len(seq) >= 1000:
            return seq, "M13mp18", False
    return _synthetic_scaffold(), "synthetic-7249", True


def fetch_m13(accession: str = "X02513.1") -> str:
    """Cache the real M13mp18 (p7249) scaffold to data/m13mp18.txt.

    The canonical 7249-nt origami scaffold (Rothemund 2006 onward) is the one shipped
    inside the `scadnano` package as `scadnano.m13()`; that is exactly the strand IDT
    plate orders fold against, so the compiler's staples must match it. Strategy:
      1. if `scadnano` is importable, use scadnano.m13() (authoritative, 7249 nt);
      2. else fall back to NCBI efetch for `accession` (M13mp18 lineage X02513).
    The compiler is scaffold-agnostic, so any valid ssDNA works; this just makes the
    emitted staples directly orderable. Requires network for the NCBI path.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    seq = None
    source = None
    try:
        import scadnano  # type: ignore
        seq = "".join(c for c in scadnano.m13().upper() if c in "ACGT")
        source = "scadnano.m13() p7249"
    except Exception:
        seq = None
    if not seq:
        import urllib.request
        url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=nuccore&id={accession}&rettype=fasta&retmode=text"
        )
        with urllib.request.urlopen(url, timeout=30) as resp:
            text = resp.read().decode("ascii", errors="ignore")
        seq = "".join(c for c in text.upper() if c in "ACGT")
        source = f"NCBI {accession}"
    if len(seq) < 1000:
        raise RuntimeError(f"fetched scaffold too short ({len(seq)} nt)")
    with open(M13_PATH, "w", encoding="utf-8") as fh:
        fh.write(f"; M13mp18 scaffold, {source}, {len(seq)} nt\n")
        fh.write(seq + "\n")
    return seq


# --------------------------------------------------------------------------- #
# Edge length assignment + Eulerian routing
# --------------------------------------------------------------------------- #
def assign_edge_bp(mesh, scaffold_budget, min_edge_bp=42, max_edge_bp=105,
                   target_edge_bp=63, round_to=1):
    """Map each mesh edge to a DNA-duplex length in bp.

    Edges are scaled so the *mean* edge is ~target_edge_bp (default 63 bp = 6 turns),
    clamped to [min_edge_bp, max_edge_bp] (42-105 bp = 4-10 turns, the practical
    wireframe range). Realistic edge lengths give physically sensible ~tens-of-nm
    structures and use only as much scaffold as the geometry needs; any leftover
    scaffold loops out as ssDNA (standard, harmless). The whole route (each edge
    traversed twice) is shrunk uniformly only if it would exceed the scaffold."""
    # key by NORMALISED edges (min,max) so route()'s (min(u,v),max(u,v)) lookups
    # always hit, even if a mesh supplied un-normalised edges.
    lengths = {(min(e), max(e)): mesh.edge_length(e) for e in mesh.edges}
    mean_len = (sum(lengths.values()) / len(lengths)) if lengths else 1.0
    scale = target_edge_bp / (mean_len or 1.0)

    def build(s):
        out = {}
        for e, L in lengths.items():
            raw = L * s
            # snap to an integer number of helical turns so crossovers stay closer to
            # in-phase (DAEDALUS-style; B-DNA ~10.5 bp/turn), respecting round_to.
            turns = max(1, round(raw / BP_PER_TURN))
            bp = int(round(turns * BP_PER_TURN / round_to)) * round_to
            out[e] = max(min_edge_bp, min(max_edge_bp, bp))
        return out

    edge_bp = build(scale)
    # shrink to fit the scaffold if necessary (each edge traversed twice)
    while 2 * sum(edge_bp.values()) > scaffold_budget and min_edge_bp > 21:
        scale *= 0.9
        min_edge_bp = max(21, min_edge_bp - 2)
        max_edge_bp = max(min_edge_bp, int(max_edge_bp * 0.9))
        edge_bp = build(scale)
    return edge_bp


def _rotation_system(mesh):
    """Cyclic order of neighbours around each vertex, derived from the (oriented) mesh
    faces: for a face corner (a, v, b), the neighbour after `a` around `v` is `b`. This
    is the rotation system an A-trail follows to route the scaffold WITHOUT crossing at
    vertices (Benson et al., Nature 523:441, 2015). Empty if the mesh has no faces."""
    if not mesh.faces:
        return {}
    succ = {v: {} for v in range(len(mesh.vertices))}
    for f in mesh.faces:
        k = len(f)
        for idx in range(k):
            a, v, b = f[(idx - 1) % k], f[idx], f[(idx + 1) % k]
            succ[v][a] = b
    return succ


def _eulerian_circuit(mesh):
    """Hierholzer's algorithm on the doubled directed multigraph (each undirected edge
    -> two opposite arcs), BIASED by the face rotation system: on leaving a vertex the
    walk prefers the next edge in the rotation (the A-trail "turn" rule), which traces
    faces and avoids crossings. Hierholzer still guarantees a SINGLE closed circuit
    covering every arc, so this is a face-aware routing with no loss of the
    single-scaffold guarantee. Falls back to arbitrary order when faces are absent.
    Returns an ordered list of arcs (u, v)."""
    if not mesh.edges:
        return []
    rot = _rotation_system(mesh)
    remaining = {v: [] for v in range(len(mesh.vertices))}
    for i, j in mesh.edges:
        remaining[i].append(j)
        remaining[j].append(i)

    start = mesh.edges[0][0]
    stack = [start]
    path = []
    while stack:
        v = stack[-1]
        nbrs = remaining[v]
        if nbrs:
            nxt = None
            if rot and len(stack) >= 2:                 # A-trail turn: next in rotation
                cand = rot.get(v, {}).get(stack[-2])
                if cand in nbrs:
                    nxt = cand
            if nxt is None:
                nxt = nbrs[-1]
            nbrs.remove(nxt)
            stack.append(nxt)
        else:
            path.append(stack.pop())
    path.reverse()
    return list(zip(path, path[1:]))


def _is_connected(mesh):
    """Are all edge-incident vertices in one connected component?"""
    if not mesh.edges:
        return True
    adj = mesh.adjacency()
    start = mesh.edges[0][0]
    seen, stack = set(), [start]
    while stack:
        v = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        stack.extend(adj[v])
    verts_with_edges = {i for e in mesh.edges for i in e}
    return verts_with_edges <= seen


def route(mesh, scaffold_seq, scaffold_name, synthetic, min_edge_bp=42):
    """Build the full scaffold Routing for a mesh."""
    if not mesh.edges:
        raise ValueError("mesh has no edges to route")
    # A single scaffold strand cannot thread separate components.
    if not _is_connected(mesh):
        raise ValueError(
            "mesh is disconnected: a single scaffold cannot route separate components. "
            "Supply a connected wireframe, or route each component as its own design."
        )
    budget = len(scaffold_seq)
    edge_bp = assign_edge_bp(mesh, budget, min_edge_bp=min_edge_bp)
    arcs = _eulerian_circuit(mesh)

    segments = []
    crossover_positions = []
    pos = 0
    truncated = False
    for order, (u, v) in enumerate(arcs):
        e = (min(u, v), max(u, v))
        bp = edge_bp[e]
        if pos + bp > len(scaffold_seq):
            bp = len(scaffold_seq) - pos
            truncated = True
            if bp <= 0:
                break
        seq = scaffold_seq[pos:pos + bp]
        segments.append(Segment(order, (u, v), e, bp, pos, seq))
        pos += bp
        crossover_positions.append(pos)  # boundary = vertex crossover

    # Every edge must be traversed exactly twice (once per direction). If the scaffold
    # ran out, the design would be silently nicked -- fail loudly instead.
    counts = {}
    for s in segments:
        counts[s.edge] = counts.get(s.edge, 0) + 1
    if truncated or set(counts) != set(mesh.edges) or any(c != 2 for c in counts.values()):
        raise ValueError(
            "scaffold too short to route this design (every edge must be covered "
            "twice). Use a longer scaffold (e.g. p8064) or a coarser/smaller mesh, "
            "or raise --min-edge-bp tolerance."
        )

    full = "".join(s.seq for s in segments)
    # crossover_positions[-1] == len(full); the optimizer filters boundaries to
    # 0 < p < S, so the closing boundary is harmless to keep (and dropping it blindly
    # would discard a real interior boundary on truncation).
    return Routing(
        scaffold_name=scaffold_name,
        scaffold_len_used=len(full),
        scaffold_seq=full,
        segments=segments,
        edge_bp=edge_bp,
        crossover_positions=crossover_positions,
        synthetic=synthetic,
    )
