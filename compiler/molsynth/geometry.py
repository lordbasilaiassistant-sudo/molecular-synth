"""
Geometry front-end for the compiler.

Loads a target shape and reduces it to the graph the scaffold router needs:
a set of 3D vertices and the undirected edges connecting them (a wireframe).

Supported inputs:
  * Built-in polyhedron presets (tetrahedron, cube, octahedron, ...) - exact,
    dependency-free, good for the end-to-end test path.
  * STL meshes (ASCII or binary) - triangle soup is welded into a vertex/edge
    wireframe. If `trimesh` is installed it is used for robust loading; otherwise
    a built-in minimal STL parser handles the common cases.
  * A simple JSON shape spec: {"vertices": [[x,y,z],...], "edges": [[i,j],...]}.

Wireframe (edge-based) DNA origami is the geometry model behind PERDIX/DAEDALUS/
vHelix (Benson 2015 Nature; Veneziano 2016 Science; Jun 2019 Sci. Adv.); see
docs/science.md. Each mesh edge becomes one DNA double-helix in the router.
"""

from __future__ import annotations

import json
import math
import struct
from dataclasses import dataclass, field


@dataclass
class Mesh:
    name: str
    vertices: list                      # list of (x, y, z)
    edges: list                         # list of (i, j) with i < j, unique
    faces: list = field(default_factory=list)  # optional list of vertex-index tuples

    def edge_length(self, e) -> float:
        a = self.vertices[e[0]]
        b = self.vertices[e[1]]
        return math.dist(a, b)

    def adjacency(self):
        adj = {v: [] for v in range(len(self.vertices))}
        for i, j in self.edges:
            adj[i].append(j)
            adj[j].append(i)
        return adj

    def summary(self) -> dict:
        degs = [len(n) for n in self.adjacency().values()]
        lengths = [self.edge_length(e) for e in self.edges]
        return {
            "name": self.name,
            "vertices": len(self.vertices),
            "edges": len(self.edges),
            "faces": len(self.faces),
            "min_degree": min(degs) if degs else 0,
            "max_degree": max(degs) if degs else 0,
            "min_edge_len": round(min(lengths), 4) if lengths else 0.0,
            "max_edge_len": round(max(lengths), 4) if lengths else 0.0,
        }


def orient_faces(faces):
    """Make all faces consistently wound (same handedness) by propagating orientation
    across the face-adjacency graph: on a correctly-oriented manifold, two faces sharing
    an edge traverse it in OPPOSITE directions; if they traverse it the same way, flip
    one. Consistent winding is what makes the A-trail rotation system a clean permutation
    at every vertex (real-world STL/PLY meshes are often inconsistently wound)."""
    from collections import deque, defaultdict
    if not faces:
        return faces
    faces = [list(f) for f in faces]
    edge_faces = defaultdict(list)
    for fi, f in enumerate(faces):
        for a, b in zip(f, f[1:] + f[:1]):
            edge_faces[frozenset((a, b))].append(fi)
    seen = [False] * len(faces)
    for start in range(len(faces)):
        if seen[start]:
            continue
        seen[start] = True
        dq = deque([start])
        while dq:
            fi = dq.popleft()
            f = faces[fi]
            dedges = set(zip(f, f[1:] + f[:1]))
            for a, b in dedges:
                for fj in edge_faces[frozenset((a, b))]:
                    if fj == fi or seen[fj]:
                        continue
                    g = faces[fj]
                    if (a, b) in set(zip(g, g[1:] + g[:1])):  # same direction -> flip
                        faces[fj] = g[::-1]
                    seen[fj] = True
                    dq.append(fj)
    return [tuple(f) for f in faces]


def _dedup_edges(raw_edges):
    seen = set()
    out = []
    for i, j in raw_edges:
        if i == j:
            continue
        key = (min(i, j), max(i, j))
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


# --------------------------------------------------------------------------- #
# Built-in polyhedron presets (unit-ish coordinates)
# --------------------------------------------------------------------------- #
def _tetrahedron() -> Mesh:
    v = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    faces = [(0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)]
    edges = _dedup_edges([(a, b) for f in faces for a, b in zip(f, f[1:] + f[:1])])
    return Mesh("tetrahedron", v, edges, faces)


def _cube() -> Mesh:
    v = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    edges = []
    for a in range(8):
        for b in range(a + 1, 8):
            # connect vertices differing in exactly one coordinate
            diff = sum(1 for k in range(3) if v[a][k] != v[b][k])
            if diff == 1:
                edges.append((a, b))
    # consistently outward-wound faces (-X,+X,-Y,+Y,-Z,+Z), so the rotation system
    # used by the A-trail routing is a clean neighbour permutation at every vertex.
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return Mesh("cube", v, _dedup_edges(edges), faces)


def _octahedron() -> Mesh:
    v = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    faces = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4),
             (0, 5, 2), (2, 5, 1), (1, 5, 3), (3, 5, 0)]
    edges = _dedup_edges([(a, b) for f in faces for a, b in zip(f, f[1:] + f[:1])])
    return Mesh("octahedron", v, edges, faces)


def _square() -> Mesh:
    """A flat square frame - the simplest 2D test wireframe."""
    v = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    edges = _dedup_edges([(0, 1), (1, 2), (2, 3), (3, 0)])  # normalize (3,0)->(0,3)
    return Mesh("square", v, edges, [(0, 1, 2, 3)])


def _icosahedron() -> Mesh:
    """Regular icosahedron — 12 vertices, 30 edges, 20 triangular faces. A real
    icosahedral nanocage shape (the geometry of many viral capsids)."""
    p = (1 + 5 ** 0.5) / 2.0
    v = [(-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0),
         (0, -1, p), (0, 1, p), (0, -1, -p), (0, 1, -p),
         (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1)]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
             (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
             (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
             (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    faces = orient_faces(faces)
    edges = _dedup_edges([(a, b) for f in faces for a, b in zip(f, f[1:] + f[:1])])
    return Mesh("icosahedron", v, edges, faces)


def _dodecahedron() -> Mesh:
    """Regular dodecahedron — 20 vertices, 30 edges, 12 pentagonal faces. Built as the
    DUAL of the (verified) icosahedron: dodeca vertices are icosa face-centroids, and
    each dodeca pentagon is the ring of faces around one icosa vertex (in rotation
    order). Derived from a correct mesh, so the topology is guaranteed right."""
    ico = _icosahedron()
    dverts = [tuple(sum(ico.vertices[i][k] for i in f) / len(f) for k in range(3))
              for f in ico.faces]
    tri_idx = {frozenset(f): fi for fi, f in enumerate(ico.faces)}
    # rotation system of the icosa: succ[v][a]=b for each face corner (a, v, b)
    rot = {v: {} for v in range(len(ico.vertices))}
    for f in ico.faces:
        n = len(f)
        for idx in range(n):
            a, vv, b = f[(idx - 1) % n], f[idx], f[(idx + 1) % n]
            rot[vv][a] = b
    dfaces = []
    for v in range(len(ico.vertices)):
        succ = rot[v]
        start = next(iter(succ))
        order, cur = [start], succ[start]
        while cur != start and len(order) < 12:
            order.append(cur)
            cur = succ[cur]
        face = []
        for k in range(len(order)):
            a, b = order[k], order[(k + 1) % len(order)]
            fi = tri_idx.get(frozenset((v, a, b)))
            if fi is not None:
                face.append(fi)
        dfaces.append(tuple(face))
    dfaces = orient_faces(dfaces)
    edges = _dedup_edges([(a, b) for f in dfaces for a, b in zip(f, f[1:] + f[:1])])
    return Mesh("dodecahedron", dverts, edges, dfaces)


PRESETS = {
    "tetrahedron": _tetrahedron,
    "cube": _cube,
    "octahedron": _octahedron,
    "icosahedron": _icosahedron,
    "dodecahedron": _dodecahedron,
    "square": _square,
}


# --------------------------------------------------------------------------- #
# STL loading
# --------------------------------------------------------------------------- #
def _weld(points, tol=1e-4):
    """Map near-identical points to a single index."""
    verts = []
    index = {}
    remap = []
    for p in points:
        key = (round(p[0] / tol), round(p[1] / tol), round(p[2] / tol))
        if key not in index:
            index[key] = len(verts)
            verts.append((float(p[0]), float(p[1]), float(p[2])))
        remap.append(index[key])
    return verts, remap


def _parse_stl_minimal(path):
    """Dependency-free STL reader (binary or ASCII). Returns (points, triangles)
    where triangles index into points before welding."""
    with open(path, "rb") as fh:
        data = fh.read()
    triangles = []
    points = []
    # Robust format detection: a binary STL is exactly 84 + 50*count bytes. Trust that
    # size invariant first (it can't be faked by an ASCII header that merely contains
    # the word "solid"); only fall back to keyword sniffing if the size doesn't match.
    is_binary = False
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if 84 + 50 * count == len(data):
            is_binary = True
    if not is_binary and (b"facet" in data or b"vertex" in data):
        # ASCII
        text = data.decode("ascii", errors="ignore")
        tri = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("vertex"):
                _, x, y, z = line.split()[:4]
                tri.append((float(x), float(y), float(z)))
                if len(tri) == 3:
                    base = len(points)
                    points.extend(tri)
                    triangles.append((base, base + 1, base + 2))
                    tri = []
    else:
        # Binary: 80-byte header, uint32 count, then 50 bytes per triangle
        count = struct.unpack_from("<I", data, 80)[0]
        off = 84
        for _ in range(count):
            vals = struct.unpack_from("<12fH", data, off)
            off += 50
            tri = [(vals[3], vals[4], vals[5]),
                   (vals[6], vals[7], vals[8]),
                   (vals[9], vals[10], vals[11])]
            base = len(points)
            points.extend(tri)
            triangles.append((base, base + 1, base + 2))
    return points, triangles


def load_stl(path) -> Mesh:
    try:
        import trimesh  # type: ignore
        m = trimesh.load(path, force="mesh")
        verts = [tuple(map(float, p)) for p in m.vertices]
        faces = [tuple(int(i) for i in f) for f in m.faces]
    except Exception:
        points, triangles = _parse_stl_minimal(path)
        verts, remap = _weld(points)
        faces = [(remap[a], remap[b], remap[c]) for a, b, c in triangles]
    raw_edges = []
    for f in faces:
        for a, b in zip(f, f[1:] + f[:1]):
            raw_edges.append((a, b))
    name = path.replace("\\", "/").split("/")[-1]
    return Mesh(name, verts, _dedup_edges(raw_edges), orient_faces(faces))


def load_ply(path) -> Mesh:
    """Minimal ASCII PLY reader (the mesh format DAEDALUS/PERDIX use). Reads the
    vertex/face elements and welds faces into a wireframe."""
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        lines = fh.read().splitlines()
    n_vert = n_face = 0
    i = 0
    while i < len(lines):
        parts = lines[i].split()
        if parts and parts[0] == "element":
            if parts[1] == "vertex":
                n_vert = int(parts[2])
            elif parts[1] == "face":
                n_face = int(parts[2])
        if lines[i].strip() == "end_header":
            i += 1
            break
        i += 1
    verts = []
    for _ in range(n_vert):
        p = lines[i].split()
        verts.append((float(p[0]), float(p[1]), float(p[2])))
        i += 1
    faces, raw_edges = [], []
    for _ in range(n_face):
        p = lines[i].split()
        cnt = int(p[0])
        f = tuple(int(x) for x in p[1:1 + cnt])
        faces.append(f)
        for a, b in zip(f, f[1:] + f[:1]):
            raw_edges.append((a, b))
        i += 1
    name = path.replace("\\", "/").split("/")[-1]
    return Mesh(name, verts, _dedup_edges(raw_edges), orient_faces(faces))


def load_json_spec(path) -> Mesh:
    with open(path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    verts = [tuple(map(float, v)) for v in spec["vertices"]]
    edges = _dedup_edges([tuple(e) for e in spec["edges"]])
    faces = [tuple(f) for f in spec.get("faces", [])]
    return Mesh(spec.get("name", path), verts, edges, orient_faces(faces))


def load_shape(spec: str) -> Mesh:
    """Dispatch on the shape argument: a preset name, an STL file, or a JSON spec."""
    key = spec.lower()
    if key in PRESETS:
        return PRESETS[key]()
    low = spec.lower()
    if low.endswith(".stl"):
        return load_stl(spec)
    if low.endswith(".ply"):
        return load_ply(spec)
    if low.endswith(".json"):
        return load_json_spec(spec)
    raise ValueError(
        f"Unknown shape '{spec}'. Use a preset {sorted(PRESETS)}, an .stl/.ply file, "
        f"or a .json wireframe spec."
    )
