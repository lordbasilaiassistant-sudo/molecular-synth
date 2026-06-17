"""
End-to-end + invariant tests for the Molecular Synth v0 compiler.
Stdlib unittest only (no pip deps). Run:

    python tests/test_compiler.py
    # or:  python -m pytest tests/
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "compiler"))

import molsynth                                   # noqa: E402
from molsynth import geometry, scaffold as sc     # noqa: E402
from molsynth import sequences as seq             # noqa: E402
from molsynth.staples import build_staples        # noqa: E402
from molsynth.optimizer import YieldModel         # noqa: E402


class TestSequences(unittest.TestCase):
    def test_reverse_complement(self):
        self.assertEqual(seq.reverse_complement("AAAA"), "TTTT")
        self.assertEqual(seq.reverse_complement("ACGT"), "ACGT")  # palindrome
        self.assertEqual(seq.reverse_complement("GGGGCCCC"), "GGGGCCCC")

    def test_tm_increases_with_gc(self):
        at = seq.tm("ATATATATATATATATAT")
        gc = seq.tm("GCGCGCGCGCGCGCGCGC")
        self.assertGreater(gc, at)

    def test_gc_content(self):
        self.assertAlmostEqual(seq.gc_content("GGCCAATT"), 0.5)

    def test_homopolymer_run(self):
        self.assertEqual(seq.max_homopolymer_run("AAATTGGGGC"), 4)


class TestGeometry(unittest.TestCase):
    def test_preset_edge_counts(self):
        self.assertEqual(len(geometry.load_shape("tetrahedron").edges), 6)
        self.assertEqual(len(geometry.load_shape("cube").edges), 12)
        self.assertEqual(len(geometry.load_shape("octahedron").edges), 12)

    def test_orient_faces_repairs_winding(self):
        """A mesh with one flipped face is re-oriented so the rotation system is a clean
        permutation again (the STL/PLY robustness fix)."""
        base = geometry.load_shape("tetrahedron")
        faces = [list(f) for f in base.faces]
        faces[0] = faces[0][::-1]                        # corrupt one face's winding
        fixed = geometry.orient_faces(faces)
        m = geometry.Mesh("t", base.vertices, base.edges, fixed)
        rot = sc._rotation_system(m)
        adj = m.adjacency()
        for v in range(len(m.vertices)):
            self.assertEqual(set(rot[v].keys()), set(adj[v]), v)
            self.assertEqual(set(rot[v].values()), set(adj[v]), v)

    def test_json_spec_roundtrip(self):
        spec = '{"name":"tri","vertices":[[0,0,0],[1,0,0],[0,1,0]],"edges":[[0,1],[1,2],[2,0]]}'
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(spec)
            path = fh.name
        try:
            m = geometry.load_shape(path)
            self.assertEqual(len(m.edges), 3)
        finally:
            os.unlink(path)


class TestRouting(unittest.TestCase):
    def test_eulerian_covers_each_edge_twice(self):
        mesh = geometry.load_shape("cube")
        s, name, synth = sc.load_scaffold()
        routing = sc.route(mesh, s, name, synth)
        counts = {}
        for segm in routing.segments:
            counts[segm.edge] = counts.get(segm.edge, 0) + 1
        # every mesh edge traversed exactly twice (closed Eulerian circuit)
        self.assertEqual(set(counts.keys()), set(mesh.edges))
        self.assertTrue(all(c == 2 for c in counts.values()), counts)

    def test_rotation_system_from_faces(self):
        """The face rotation system (the A-trail turn order) is a clean permutation of
        each vertex's neighbours on EVERY closed preset (needs consistently-wound faces)."""
        for shape in ("tetrahedron", "cube", "octahedron"):
            mesh = geometry.load_shape(shape)
            rot = sc._rotation_system(mesh)
            adj = mesh.adjacency()
            for v in range(len(mesh.vertices)):
                self.assertEqual(set(rot[v].keys()), set(adj[v]), (shape, v))
                self.assertEqual(set(rot[v].values()), set(adj[v]), (shape, v))

    def test_disconnected_mesh_rejected(self):
        """A single scaffold cannot route separate components -> must raise, not
        silently drop edges."""
        spec = ('{"name":"disc","vertices":[[0,0,0],[1,0,0],[5,5,5],[6,5,5]],'
                '"edges":[[0,1],[2,3]]}')
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write(spec)
            path = fh.name
        try:
            mesh = geometry.load_shape(path)
            s, name, synth = sc.load_scaffold()
            with self.assertRaises(ValueError):
                sc.route(mesh, s, name, synth)
        finally:
            os.unlink(path)


class TestStaples(unittest.TestCase):
    def setUp(self):
        mesh = geometry.load_shape("cube")
        s, name, synth = sc.load_scaffold()
        self.routing = sc.route(mesh, s, name, synth)
        self.staples, self.history = build_staples(
            self.routing, YieldModel(), iterations=3000, seed=1)

    def test_length_bounds(self):
        for st in self.staples:
            self.assertGreaterEqual(st.length, 32)
            self.assertLessEqual(st.length, 42)

    def test_staples_are_reverse_complement_of_scaffold(self):
        """Chemical validity: each staple must be the exact reverse complement of
        the scaffold region it spans, or it will not hybridise."""
        route = self.routing.scaffold_seq
        for st in self.staples:
            region = route[st.scaffold_start:st.scaffold_end]
            self.assertEqual(st.seq, seq.reverse_complement(region),
                             f"{st.name} not RC of its scaffold span")

    def test_optimizer_improves(self):
        self.assertLessEqual(self.history[-1], self.history[0])

    def test_proxy_score_runs(self):
        from molsynth.optimizer import proxy_score
        sc_score = proxy_score(self.routing, YieldModel())
        self.assertIsInstance(sc_score, float)
        self.assertGreater(sc_score, 0)

    def test_wells_unique(self):
        wells = [st.well for st in self.staples]
        self.assertEqual(len(wells), len(set(wells)))


class TestScience(unittest.TestCase):
    """Anchor the numerics to the literature, not just to ourselves."""

    def test_nn_params_match_santalucia_1998(self):
        # Spot-check published unified NN values (PNAS 95:1460, Table 1).
        self.assertEqual(seq.NN_PARAMS["AA"], (-7.9, -22.2))
        self.assertEqual(seq.NN_PARAMS["CG"], (-10.6, -27.2))
        self.assertEqual(seq.NN_PARAMS["GC"], (-9.8, -24.4))
        self.assertEqual(seq.NN_PARAMS["TA"], (-7.2, -21.3))
        self.assertEqual(seq.INIT_GC, (0.1, -2.8))
        self.assertEqual(seq.INIT_AT, (2.3, 4.1))

    def test_nn_complement_symmetry(self):
        # NN(XY) must equal NN(revcomp(XY)) under the model's expansion.
        for k, v in seq.NN_PARAMS.items():
            rc = seq.reverse_complement(k)
            self.assertEqual(seq.NN_PARAMS[rc], v, f"{k} vs {rc}")

    def test_tm_physical_range(self):
        # a ~36 nt, ~50% GC staple should melt in a physically sane band
        s = "ACGTACGTACGTGGCCAATTGGCCAATTACGTACGT"
        t = seq.tm(s)
        self.assertTrue(40 < t < 85, t)

    def test_cross_dimer_detection(self):
        a = "ACGTACGTAA"
        self.assertEqual(seq.cross_dimer_len(a, seq.reverse_complement(a)), len(a))
        self.assertEqual(seq.cross_dimer_len("AAAAAAAAAA", "AAAAAAAAAA"), 0)  # A vs A: no complement
        self.assertEqual(seq.lcs_len("ABCDEF", "ZBCDEZ"), 4)                  # "BCDE"

    def test_repeat_mask_and_longest_run(self):
        rep, mid = "ACGTACGTAC", "TTGGAACCAA"
        s = rep + mid + rep            # the rep stretch is duplicated; mid is unique
        m = seq.repeat_mask(s, k=8)
        self.assertTrue(m[5])          # inside a duplicated stretch -> flagged
        self.assertFalse(m[14])        # unique middle -> not flagged
        self.assertGreaterEqual(seq.longest_run(m, 0, 10), 8)

    def test_offtarget_screen_controls_repeats(self):
        """The compiler keeps long scaffold-repeats from concentrating in one staple."""
        with tempfile.TemporaryDirectory() as d:
            summary = molsynth.compile_shape("cube", outdir=d, iterations=4000)
            st = summary["staple_stats"]
            self.assertIn("offtarget_max", st)
            self.assertLessEqual(st["offtarget_max"], 22)   # no runaway off-target staple

    def test_stl_roundtrip(self):
        stl = os.path.join(ROOT, "examples", "octahedron.stl")
        if not os.path.exists(stl):
            self.skipTest("octahedron.stl not generated")
        m = geometry.load_shape(stl)
        self.assertEqual(len(m.vertices), 6)
        self.assertEqual(len(m.edges), 12)

    def test_ply_roundtrip(self):
        ply = ("ply\nformat ascii 1.0\nelement vertex 4\n"
               "property float x\nproperty float y\nproperty float z\n"
               "element face 4\nproperty list uchar int vertex_indices\n"
               "end_header\n1 1 1\n1 -1 -1\n-1 1 -1\n-1 -1 1\n"
               "3 0 1 2\n3 0 3 1\n3 0 2 3\n3 1 3 2\n")
        with tempfile.NamedTemporaryFile("w", suffix=".ply", delete=False) as fh:
            fh.write(ply)
            path = fh.name
        try:
            m = geometry.load_shape(path)
            self.assertEqual(len(m.vertices), 4)
            self.assertEqual(len(m.edges), 6)   # tetrahedron
        finally:
            os.unlink(path)


class TestStructure3D(unittest.TestCase):
    def setUp(self):
        from molsynth import structure3d
        self.structure3d = structure3d
        self.mesh = geometry.load_shape("tetrahedron")
        s, name, synth = sc.load_scaffold()
        self.routing = sc.route(self.mesh, s, name, synth)
        self.staples, _ = build_staples(self.routing, YieldModel(), iterations=800, seed=3)
        self.nucs, self.box = structure3d.build_structure(
            self.mesh, self.routing, self.staples)

    def test_nucleotide_count(self):
        expected = len(self.routing.scaffold_seq) + sum(len(s.seq) for s in self.staples)
        self.assertEqual(len(self.nucs), expected)

    def test_frames_orthonormal(self):
        rep = self.structure3d.orthonormal_report(self.nucs)
        self.assertLess(rep["max_unit_dev"], 1e-6, rep)
        self.assertLess(rep["max_orth_dev"], 1e-6, rep)

    def test_duplex_geometry_not_inverted(self):
        """Regression for the a1-inversion bug: paired backbones must sit OUTSIDE
        (far apart) and bases meet near the axis (close) -- not the reverse."""
        rep = self.structure3d.duplex_report(self.mesh, self.routing)
        bb = rep["mean_backbone_pair_dist"]
        base = rep["mean_base_pair_dist"]
        self.assertGreater(bb, base, rep)          # backbones outside, bases inside
        self.assertGreater(bb, 0.34, rep)          # above oxDNA excluded-volume floor
        self.assertLess(base, bb, rep)
        self.assertAlmostEqual(bb, 1.2, delta=0.15, msg=rep)   # ~2*BACKBONE_R

    def test_topology_config_consistent(self):
        """conf.dat body length must equal the .top nucleotide count."""
        from molsynth import export
        with tempfile.TemporaryDirectory() as d:
            top, conf = export.write_oxdna(d, self.nucs, self.box)
            top_lines = open(top).read().splitlines()
            conf_lines = open(conf).read().splitlines()
            nbases = int(top_lines[0].split()[0])
            self.assertEqual(len(top_lines) - 1, nbases)
            self.assertEqual(len(conf_lines) - 3, nbases)   # 3 header lines
            # every config row has the 15 oxDNA columns
            for row in conf_lines[3:]:
                self.assertEqual(len(row.split()), 15)


class TestDecorate(unittest.TestCase):
    """Rung 2: functional handle staples (DNA breadboard)."""

    def setUp(self):
        from molsynth import decorate as decorate_mod
        self.decorate_mod = decorate_mod
        self.mesh = geometry.load_shape("cube")
        s, name, synth = sc.load_scaffold()
        self.routing = sc.route(self.mesh, s, name, synth)
        self.staples, _ = build_staples(self.routing, YieldModel(), iterations=600, seed=4)

    def test_handles_orthogonal_and_absent_from_scaffold(self):
        scaf = self.routing.scaffold_seq
        handles = self.decorate_mod.generate_handles(scaf, n=12)
        self.assertGreaterEqual(len(handles), 8)
        for h in handles:
            self.assertNotIn(h, scaf)
            self.assertNotIn(seq.reverse_complement(h), scaf)
        # pairwise low cross-hybridisation
        for i in range(len(handles)):
            for j in range(len(handles)):
                if i != j:
                    cross = self.decorate_mod._lcs_len(
                        seq.reverse_complement(handles[i]), handles[j])
                    self.assertLess(cross, 7, (i, j))

    def test_decorate_preserves_binding_and_extends_order_seq(self):
        records = self.decorate_mod.decorate(self.staples, self.routing, 3,
                                             guests=["E1", "E2", "E3"])
        self.assertEqual(len(records), 3)
        route = self.routing.scaffold_seq
        decorated = [s for s in self.staples if s.handle]
        self.assertEqual(len(decorated), 3)
        for s in decorated:
            # binding region unchanged -> still the exact reverse complement (chem valid)
            region = route[s.scaffold_start:s.scaffold_end]
            self.assertEqual(s.seq, seq.reverse_complement(region))
            # order sequence = binding + spacer + handle (3' end)
            self.assertEqual(s.order_seq, s.seq + s.spacer + s.handle)
            self.assertTrue(s.order_seq.endswith(s.handle))

    def test_anti_handle_is_reverse_complement(self):
        records = self.decorate_mod.decorate(self.staples, self.routing, 2)
        for r in records:
            self.assertEqual(r["anti_handle"], seq.reverse_complement(r["handle"]))

    def test_cascade_orders_guests_and_measures_spacing(self):
        recs = self.decorate_mod.decorate_cascade(
            self.staples, self.routing, self.mesh, ["GOx", "HRP", "catalase"],
            spacing_nm=10)
        self.assertEqual(len(recs), 3)
        self.assertEqual([r["guest"] for r in recs], ["GOx", "HRP", "catalase"])
        self.assertEqual(recs[0]["spacing_nm"], 0.0)        # first site = reference
        for r in recs[1:]:
            self.assertGreater(r["spacing_nm"], 0)          # real measured 3D distance


class TestEndToEnd(unittest.TestCase):
    def test_compile_writes_all_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            summary = molsynth.compile_shape("tetrahedron", outdir=d, iterations=2000)
            for f in ("scaffold.fasta", "staples.csv", "staples_idt_plate.txt",
                      "staples_opool.txt", "design.json", "design.top", "conf.dat",
                      "structure.pdb", "oxdna_min.input", "oxdna_relax.input",
                      "shape.ply", "protocol.md", "diagnostics.md", "screen.md"):
                self.assertTrue(os.path.exists(os.path.join(d, f)), f)
            self.assertGreater(summary["n_staples"], 0)
            self.assertGreater(summary["approx_nm"], 0)

    def test_all_presets_compile(self):
        """Every built-in preset must route + compile end-to-end (square regressed once)."""
        import tempfile
        for shape in ("tetrahedron", "cube", "octahedron", "square"):
            with tempfile.TemporaryDirectory() as d:
                summary = molsynth.compile_shape(shape, outdir=d, iterations=400)
                self.assertGreater(summary["n_staples"], 0, shape)

    def test_shape_ply_roundtrips(self):
        """The emitted shape.ply (PERDIX/DAEDALUS hand-off) re-parses to the same mesh."""
        from molsynth import export, geometry
        mesh = geometry.load_shape("octahedron")
        with tempfile.TemporaryDirectory() as d:
            path = export.write_ply(d, mesh)
            back = geometry.load_shape(path)
            self.assertEqual(len(back.vertices), len(mesh.vertices))
            self.assertEqual(len(back.edges), len(mesh.edges))

    def test_oxdna_topology_header(self):
        mesh = geometry.load_shape("tetrahedron")
        s, name, synth = sc.load_scaffold()
        routing = sc.route(mesh, s, name, synth)
        staples, _ = build_staples(routing, YieldModel(), iterations=1000, seed=2)
        from molsynth import export
        with tempfile.TemporaryDirectory() as d:
            path = export.write_oxdna_topology(d, routing, staples)
            with open(path) as fh:
                lines = fh.read().splitlines()
            nbases, nstrands = map(int, lines[0].split())
            self.assertEqual(nstrands, 1 + len(staples))
            self.assertEqual(len(lines) - 1, nbases)  # one row per nucleotide


if __name__ == "__main__":
    unittest.main(verbosity=2)
