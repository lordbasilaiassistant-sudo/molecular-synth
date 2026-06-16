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


class TestEndToEnd(unittest.TestCase):
    def test_compile_writes_all_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            summary = molsynth.compile_shape("tetrahedron", outdir=d, iterations=2000)
            for f in ("scaffold.fasta", "staples.csv", "staples_idt_plate.txt",
                      "staples_opool.txt", "design.json", "design.top", "conf.dat",
                      "structure.pdb", "oxdna_min.input", "oxdna_relax.input",
                      "protocol.md", "diagnostics.md", "screen.md"):
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
