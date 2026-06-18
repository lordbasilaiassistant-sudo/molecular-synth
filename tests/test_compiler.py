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
        self.assertEqual(len(geometry.load_shape("icosahedron").edges), 30)
        d = geometry.load_shape("dodecahedron")
        self.assertEqual((len(d.vertices), len(d.edges), len(d.faces)), (20, 30, 12))
        self.assertTrue(all(len(f) == 5 for f in d.faces))   # pentagons

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

    def test_single_scaffold_circuit_invariant(self):
        """The defining physical premise: every preset routes as ONE closed scaffold loop
        covering each edge twice, once per direction. Machine-checked, not just claimed."""
        s, name, synth = sc.load_scaffold()
        for shape in ("tetrahedron", "cube", "octahedron", "icosahedron",
                      "dodecahedron", "square"):
            mesh = geometry.load_shape(shape)
            arcs = sc._eulerian_circuit(mesh)
            rep = sc.circuit_report(arcs, mesh.edges)
            self.assertTrue(rep["single_circuit"], (shape, rep))
            self.assertEqual(rep["n_arcs"], 2 * len(mesh.edges), shape)
            self.assertTrue(sc.route(mesh, s, name, synth).single_circuit, shape)

    def test_circuit_report_rejects_broken_trails(self):
        """A trail that is open, incomplete, or discontinuous is NOT a single circuit."""
        edges = [(0, 1), (1, 2), (2, 0)]
        good = [(0, 1), (1, 2), (2, 0), (0, 2), (2, 1), (1, 0)]
        self.assertTrue(sc.circuit_report(good, edges)["single_circuit"])
        # missing the closing arc -> not closed / not complete
        self.assertFalse(sc.circuit_report(good[:-1], edges)["single_circuit"])
        # a discontinuous jump (0->2 without sharing the prior arc's head)
        bad = [(0, 1), (1, 0), (2, 0), (0, 2), (1, 2), (2, 1)]
        self.assertFalse(sc.circuit_report(bad, edges)["single_circuit"])

    def test_vertex_crossing_metric_is_measured_and_honest(self):
        """A-trail quality is measured, not claimed. The metric counts a vertex passage as
        non-crossing iff it turns to an edge ADJACENT in the planar rotation (next or prev
        neighbour) -- the physically correct A-trail condition (Benson 2015). The production
        router (_atrail_circuit) searches for the fewest true crossings, so every closed
        preset must come out near-perfect: counts are consistent, and crossings are few."""
        s, name, synth = sc.load_scaffold()
        for shape in ("tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron"):
            mesh = geometry.load_shape(shape)
            arcs = sc._atrail_circuit(mesh)
            rep = sc.vertex_crossings(mesh, arcs)
            self.assertEqual(rep["passages"], 2 * len(mesh.edges), shape)
            self.assertEqual(rep["crossings"] + rep["face_following"], rep["passages"], shape)
            # consistency + range; no F-1 floor (that was the stricter successor-only metric)
            self.assertGreaterEqual(rep["crossings"], 0, (shape, rep))
            self.assertTrue(0.0 < rep["face_follow_fraction"] <= 1.0, (shape, rep))
            routing = sc.route(mesh, s, name, synth)
            self.assertEqual(routing.vertex_crossings, rep["crossings"], shape)

    def test_atrail_router_beats_plain_eulerian_on_crossings(self):
        """Issue #1: the searched A-trail router yields a near-perfect, production-grade
        routing -- a handful of true vertex crossings at most, far fewer than the plain
        rotation-successor Eulerian walk -- while staying a single closed scaffold circuit.
        Ceilings are the measured count of the deterministic (seeded) router; allow a small
        margin so the test is stable across platforms without being vacuous."""
        ceilings = {"tetrahedron": 2, "cube": 2, "octahedron": 3,
                    "icosahedron": 3, "dodecahedron": 3}
        sum_atrail = sum_plain = 0
        for shape, ceil in ceilings.items():
            mesh = geometry.load_shape(shape)
            a_atrail = sc._atrail_circuit(mesh)
            a_plain = sc._eulerian_circuit(mesh)
            self.assertTrue(sc.circuit_report(a_atrail, mesh.edges)["single_circuit"], shape)
            c_atrail = sc.vertex_crossings(mesh, a_atrail)["crossings"]
            c_plain = sc.vertex_crossings(mesh, a_plain)["crossings"]
            self.assertLessEqual(c_atrail, ceil, (shape, c_atrail))      # near-perfect
            self.assertLessEqual(c_atrail, c_plain, (shape, c_atrail, c_plain))  # never worse
            sum_atrail += c_atrail
            sum_plain += c_plain
        # aggregate: the search more than halves the total crossings across the presets
        self.assertLess(sum_atrail * 2, sum_plain, (sum_atrail, sum_plain))

    def test_rotation_system_from_faces(self):
        """The face rotation system (the A-trail turn order) is a clean permutation of
        each vertex's neighbours on EVERY closed preset (needs consistently-wound faces)."""
        for shape in ("tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron"):
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

    def test_staples_partition_the_scaffold_exactly(self):
        """Physical-coherence invariant: the staple spans must EXACTLY tile the scaffold --
        every scaffold base covered by exactly one staple base, no gaps (unpaired scaffold)
        and no overlaps (a base two staples fight over). This is what makes the design
        actually foldable, proven directly on the compiler output (not via an export)."""
        S = len(self.routing.scaffold_seq)
        spans = sorted((st.scaffold_start, st.scaffold_end) for st in self.staples)
        # contiguous cover of [0, S): each span starts where the previous ended
        self.assertEqual(spans[0][0], 0, "first staple must start at scaffold base 0")
        self.assertEqual(spans[-1][1], S, "last staple must end at the scaffold's end")
        for (a0, b0), (a1, b1) in zip(spans, spans[1:]):
            self.assertEqual(b0, a1, f"gap/overlap between {b0} and {a1}")
        # total staple bases == scaffold bases (no base counted twice or missed)
        self.assertEqual(sum(b - a for a, b in spans), S)

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

    def test_equalize_tm_tightens_and_preserves_guarantees(self):
        """The Tm-equalisation pass (issue #6) must lower (or hold) the staple Tm spread
        while preserving every hard guarantee: lengths in [lo,hi], no reduced crossover
        coverage, no new loop-closure overload."""
        import math
        from molsynth import sequences as sq2
        from molsynth.optimizer import YieldModel, equalize_tm, boundaries_in
        model = YieldModel()
        w = model.weights
        lo, hi = w["len_lo"], w["len_hi"]
        template = sq2.reverse_complement(self.routing.scaffold_seq)
        S = len(template)
        xovers_t = sorted(S - p for p in self.routing.crossover_positions if 0 < p < S)
        # a valid even partition as the (pre-equalisation) starting cuts
        n = max(2, round(S / 37))
        cuts0 = sorted(set(round(S * k / n) for k in range(1, n)))

        def spans(cs):
            out, prev = [], 0
            for c in list(cs) + [S]:
                out.append((prev, c))
                prev = c
            return out

        def stdev(cs):
            ts = [sq2.tm(template[a:b]) for a, b in spans(cs)]
            ts = [t for t in ts if not math.isnan(t)]
            mu = sum(ts) / len(ts)
            return math.sqrt(sum((t - mu) ** 2 for t in ts) / len(ts))

        def coverage(cs):
            cov = set()
            for a, b in spans(cs):
                cov.update(boundaries_in(a, b, xovers_t))
            return len(cov)

        def overload(cs):
            return sum(max(0, len(boundaries_in(a, b, xovers_t)) - w["xmax"])
                       for a, b in spans(cs))

        cuts1 = equalize_tm(template, cuts0, xovers_t, model)
        self.assertLessEqual(stdev(cuts1), stdev(cuts0) + 1e-9)       # tighter or held
        self.assertTrue(all(lo <= (b - a) <= hi for a, b in spans(cuts1)))  # length bounds
        self.assertGreaterEqual(coverage(cuts1), coverage(cuts0))     # coverage not reduced
        self.assertLessEqual(overload(cuts1), overload(cuts0))        # loop-balance held

    def test_equalize_never_worsens_the_optimizer_objective(self):
        """Regression guard (found by experiment): equalize_tm tightens Tm STDEV, but that
        is only one objective term -- pushing it too far can raise the Tm-window penalty and
        net-degrade predicted yield. anneal() must therefore keep the refinement ONLY when it
        improves the FULL score, so the post-pass can never worsen what the SA achieved.
        (Before the fix this regressed the proxy on every small preset.)"""
        import molsynth.optimizer as opt
        from molsynth import sequences as sq2
        from molsynth.optimizer import YieldModel, anneal
        model = YieldModel()
        for shape in ("tetrahedron", "cube", "octahedron", "icosahedron"):
            mesh = geometry.load_shape(shape)
            s, name, synth = sc.load_scaffold()
            routing = sc.route(mesh, s, name, synth)
            template = sq2.reverse_complement(routing.scaffold_seq)
            mask = sq2.repeat_mask(routing.scaffold_seq)[:len(template)]
            kw = dict(iterations=2000, seed=11, offtarget_mask=mask)
            with_eq = anneal(template, routing.crossover_positions, model, **kw)[3][-1]
            orig = opt.equalize_tm
            opt.equalize_tm = lambda *a, **k: a[1]      # disable -> pure SA
            try:
                sa_only = anneal(template, routing.crossover_positions, model, **kw)[3][-1]
            finally:
                opt.equalize_tm = orig
            self.assertLessEqual(with_eq, sa_only + 1e-6,
                                 f"{shape}: equalize worsened the objective {sa_only}->{with_eq}")


class TestKineticLadder(unittest.TestCase):
    """Rung 3: the OPTIONAL kinetic folding-ORDER term (w_kinetic, default 0).

    The default objective is thermodynamic (equilibrium Tm clustering); this term programs
    folding ORDER, rewarding a Tm gradient where high crossover-/loop-load staples (the
    seams) are NOT the hottest, so the framework nucleates first (Dunn 2015; Sobczak 2012).
    KINETIC PROXY -- no MD simulator. See research/exp9_kinetic_ladder.py."""

    def _design(self, shape="cube"):
        mesh = geometry.load_shape(shape)
        s, name, synth = sc.load_scaffold()
        routing = sc.route(mesh, s, name, synth)
        template = seq.reverse_complement(routing.scaffold_seq)
        S = len(template)
        from molsynth.optimizer import boundaries_in
        xovers_t = sorted(S - p for p in routing.crossover_positions if 0 < p < S)
        n = max(2, round(S / 37))
        cuts = sorted(set(round(S * k / n) for k in range(1, n)))
        spans, prev = [], 0
        for c in list(cuts) + [S]:
            spans.append((prev, c))
            prev = c
        seqs, counts, loops, loop_loads, cov = [], [], [], [], set()
        for a, b in spans:
            seqs.append(template[a:b])
            bnds = boundaries_in(a, b, xovers_t)
            counts.append(len(bnds))
            cov.update(bnds)
            pts = [a] + bnds + [b]
            seg = [pts[i] - pts[i - 1] for i in range(1, len(pts))]
            loops.extend(seg)
            loop_loads.append(max(seg) if seg else 0)
        return seqs, counts, loops, loop_loads, len(xovers_t), len(cov)

    def test_w_kinetic_zero_is_byte_identical(self):
        """Existing behaviour MUST be byte-identical with the term OFF: a default model
        (w_kinetic=0) scores EXACTLY the same as a model with the kinetic keys removed
        entirely (i.e. the pre-rung-3 objective), regardless of whether per-staple loop
        loads are passed."""
        seqs, counts, loops, loop_loads, nb, ncov = self._design()
        default = YieldModel()                                  # w_kinetic=0 default
        legacy = YieldModel()
        del legacy.weights["w_kinetic"]
        del legacy.weights["kinetic_loop_w"]                    # simulate pre-rung-3 model
        s_default = default.score_set(seqs, counts, loops, nb, ncov)
        s_legacy = legacy.score_set(seqs, counts, loops, nb, ncov)
        s_with_loads = default.score_set(seqs, counts, loops, nb, ncov,
                                         staple_loop_loads=loop_loads)
        self.assertEqual(s_default, s_legacy)                   # exact, not approximate
        self.assertEqual(s_default, s_with_loads)               # loop loads are inert when OFF

    def test_kinetic_penalty_orders_framework_before_seam(self):
        """The penalty (deterministic) must favour a framework-first ladder: high-load
        staples at the COOL end cost 0; the same Tm multiset with high-load staples at the
        HOT end (a kinetic trap) costs strictly more."""
        from molsynth.optimizer import kinetic_penalty
        cross = [0, 1, 1]
        seam_first = kinetic_penalty(cross, [55.0, 60.0, 65.0])      # crossover staples hottest
        framework_first = kinetic_penalty(cross, [65.0, 55.0, 60.0])  # crossover staples coolest
        self.assertEqual(framework_first, 0.0)                  # desired gradient is free
        self.assertGreater(seam_first, framework_first)         # the trap is penalised
        # trivial inputs are zero (no spurious penalty)
        self.assertEqual(kinetic_penalty([], []), 0.0)
        self.assertEqual(kinetic_penalty([1], [60.0]), 0.0)

    def test_enabling_kinetic_reorders_tm_vs_crossload(self):
        """Enabling the term MEASURABLY reorders the Tm-vs-crossover-load relationship: on a
        design whose default optimum has a positive load->Tm covariance, turning w_kinetic on
        drives that covariance (and the load-Tm correlation) DOWN -- seam staples pushed
        cooler. Reproducible at a fixed shape/seed/iteration (cube, seed 12345, 3000)."""
        import math
        from molsynth.optimizer import anneal, boundaries_in, kinetic_penalty

        def measure(w_kinetic):
            model = YieldModel()
            model.weights["w_kinetic"] = w_kinetic
            mesh = geometry.load_shape("cube")
            s, name, synth = sc.load_scaffold()
            routing = sc.route(mesh, s, name, synth)
            template = seq.reverse_complement(routing.scaffold_seq)
            S = len(template)
            mask = seq.repeat_mask(routing.scaffold_seq)[:S]
            xovers_t = sorted(S - p for p in routing.crossover_positions if 0 < p < S)
            cuts, seqs, counts, hist = anneal(
                template, routing.crossover_positions, model,
                iterations=3000, seed=12345, offtarget_mask=mask)
            spans, prev = [], 0
            for c in list(cuts) + [S]:
                spans.append((prev, c))
                prev = c
            cross, loop_loads, tms = [], [], []
            for a, b in spans:
                bnds = boundaries_in(a, b, xovers_t)
                cross.append(len(bnds))
                pts = [a] + bnds + [b]
                segl = [pts[i] - pts[i - 1] for i in range(1, len(pts))]
                loop_loads.append(max(segl) if segl else 0)
                tms.append(seq.tm(template[a:b]))
            return kinetic_penalty(cross, tms, loop_loads=loop_loads)

        off = measure(0.0)
        on = measure(8.0)
        self.assertGreater(off, 0.0, "control: the default optimum must have a load-Tm "
                                     "inversion for there to be something to fix")
        self.assertLess(on, off,
                        f"enabling w_kinetic must lower the load-Tm covariance ({off}->{on})")


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

    def test_design_matches_published_wireframe_envelopes(self):
        """Digital half of wet-lab validation (#7): each preset's parameters sit inside the
        envelopes of experimentally-folded wireframe origami (Veneziano 2016 DAEDALUS,
        Science 352:1534; Benson 2015, Nature 523:441) -- edges on integer helical turns
        (in-phase crossovers), >= 31 bp / >= 10 nm, staples 21-78 nt, scaffold <= M13."""
        BP_PER_TURN, NM_PER_BP, M13 = 10.5, 0.34, 7249
        s, name, synth = sc.load_scaffold()
        for shape in ("tetrahedron", "cube", "octahedron", "icosahedron", "dodecahedron"):
            mesh = geometry.load_shape(shape)
            r = sc.route(mesh, s, name, synth)
            stp, _ = build_staples(r, YieldModel(), iterations=600, seed=7)
            ebp = sorted(r.edge_bp.values())
            phase = max(abs(bp - round(bp / BP_PER_TURN) * BP_PER_TURN) for bp in ebp)
            slen = sorted(len(x.seq) for x in stp)
            self.assertGreaterEqual(ebp[0], 31, (shape, "edge < DAEDALUS min"))
            self.assertLessEqual(phase, 0.75, (shape, "crossover out of phase"))
            self.assertGreaterEqual(ebp[0] * NM_PER_BP, 10.0, shape)
            self.assertGreaterEqual(slen[0], 21, (shape, "staple too short to bind"))
            self.assertLessEqual(slen[-1], 78, (shape, "staple too long to synthesise cheaply"))
            self.assertLessEqual(r.scaffold_len_used, M13, (shape, "exceeds M13"))

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
                      "shape.ply", "design_cadnano.json", "protocol.md",
                      "diagnostics.md", "screen.md"):
                self.assertTrue(os.path.exists(os.path.join(d, f)), f)
            self.assertGreater(summary["n_staples"], 0)
            self.assertGreater(summary["approx_nm"], 0)

    def test_all_presets_compile(self):
        """Every built-in preset must route + compile end-to-end (square regressed once)."""
        import tempfile
        for shape in ("tetrahedron", "cube", "octahedron", "icosahedron",
                      "dodecahedron", "square"):
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

    def test_cadnano_export_roundtrips(self):
        """The caDNAno v2 JSON decodes back (independent reader) to exactly one closed
        scaffold loop of the right length + the right staples, with reciprocal pointers
        and a complete base-pairing partition -- a verified, faithful encoding."""
        import json
        from molsynth import export
        mesh = geometry.load_shape("cube")
        s, name, synth = sc.load_scaffold()
        routing = sc.route(mesh, s, name, synth)
        staples, _ = build_staples(routing, YieldModel(), iterations=800, seed=3)
        with tempfile.TemporaryDirectory() as d:
            path = export.write_cadnano(d, routing, staples)
            rep = export.cadnano_decode(json.load(open(path)))
        self.assertTrue(rep["scaffold_closed_loop"])
        self.assertEqual(rep["scaffold_len"], routing.scaffold_len_used)
        self.assertEqual(rep["n_staples"], len(staples))
        self.assertEqual(rep["staple_lens"], sorted(len(st.seq) for st in staples))
        self.assertTrue(rep["staples_partition_complement"])
        self.assertTrue(rep["pointers_reciprocal"])

    def test_scadnano_export_loads_as_valid_origami(self):
        """If scadnano is installed, the emitted design.sc must load back through the REAL
        scadnano library (not our own reader) as exactly ONE is_scaffold strand of the
        right length plus K base-paired staples -- i.e. a valid, editable origami, not a
        pile of disconnected fragments. Skipped cleanly when scadnano isn't installed."""
        try:
            import scadnano as scn  # noqa: F401
        except Exception:
            self.skipTest("scadnano not installed")
        from molsynth import export
        mesh = geometry.load_shape("octahedron")
        s, name, synth = sc.load_scaffold()
        routing = sc.route(mesh, s, name, synth)
        staples, _ = build_staples(routing, YieldModel(), iterations=600, seed=5)
        with tempfile.TemporaryDirectory() as d:
            path = export.write_scadnano(d, routing, staples)
            self.assertIsNotNone(path, "scadnano export returned None despite being installed")
            design = scn.Design.from_scadnano_file(path)
            scaf = [x for x in design.strands if x.is_scaffold]
            stap = [x for x in design.strands if not x.is_scaffold]
            self.assertEqual(len(scaf), 1, "must be exactly one scaffold strand")
            self.assertEqual(len(stap), len(staples), "every staple present as its own strand")
            scaf_len = sum(dom.dna_length() for dom in scaf[0].domains)
            self.assertEqual(scaf_len, routing.scaffold_len_used)

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

    def test_oxdna_structure_reads_in_oat(self):
        """If oxDNA_analysis_tools is installed, the emitted design.top + conf.dat must read
        back through the REAL oat reader with the right base count and finite coordinates --
        i.e. a structure oxDNA/oxView will actually load and relax, not a malformed file.
        Skipped cleanly when oat isn't installed (it is an optional, heavy dependency)."""
        try:
            from oxDNA_analysis_tools.UTILS.RyeReader import describe, get_confs
        except Exception:
            self.skipTest("oxDNA_analysis_tools not installed")
        from molsynth import compile_shape
        with tempfile.TemporaryDirectory() as d:
            compile_shape("tetrahedron", outdir=d, iterations=400, scaffold_search=1)
            top = os.path.join(d, "design.top")
            conf = os.path.join(d, "conf.dat")
            ti, di = describe(top, conf)
            confs = get_confs(di.idxs, di.path, 0, 1, ti.nbases)
            pos = confs[0].positions
            self.assertGreater(ti.nbases, 0)
            self.assertEqual(len(pos), ti.nbases)              # one position per base
            import math
            self.assertTrue(all(math.isfinite(c) for p in pos for c in p))  # no NaN/Inf


class TestPhysicsRealityCheck(unittest.TestCase):
    """The adversarial physics/materials audit: failure modes that break the REAL build even
    when the compile succeeds (edge stiffness, G-quadruplex, buffer Tm). See research/exp6."""

    def test_g_quadruplex_screen(self):
        from molsynth import sequences as sq
        self.assertGreaterEqual(sq.g_quadruplex_sites("GGGTTAGGGTTAGGGTTAGGG"), 1)  # canonical G4
        self.assertEqual(sq.g_quadruplex_sites("ACGTACGTACGTACGTACGTACGT"), 0)      # clean

    def test_buffer_tm_is_hotter_than_default(self):
        from molsynth import sequences as sq
        s = "GCATGCATGCATGCATGCATGCATGCATGCAT"
        # 12.5 mM Mg2+ stabilises the duplex vs the 50 mM-Na default -> several deg hotter
        self.assertGreater(sq.tm_buffer(s), sq.tm(s, na_M=0.05) + 3.0)

    def test_wlc_bend_follows_sqrt_law(self):
        from molsynth import sequences as sq
        b1, b2 = sq.wlc_rms_bend_deg(63), sq.wlc_rms_bend_deg(126)
        self.assertAlmostEqual(b2 / b1, 2 ** 0.5, places=3)   # <theta^2> = L/Lp
        self.assertEqual(sq.wlc_rms_bend_deg(0), 0.0)
        self.assertGreater(b1, 25)                            # 63 bp single duplex is floppy

    def test_diagnostics_emits_reality_check(self):
        from molsynth import compile_shape
        with tempfile.TemporaryDirectory() as d:
            compile_shape("tetrahedron", outdir=d, iterations=300, scaffold_search=1)
            txt = open(os.path.join(d, "diagnostics.md"), encoding="utf-8").read()
            self.assertIn("Physics & materials reality check", txt)
            self.assertIn("edge stiffness", txt)
            self.assertIn("buffer Tm", txt)


class TestEdgeStiffnessDial(unittest.TestCase):
    """Rung 1: stiffness as a first-class design dial (multi-helix-bundle edges).

    exp6 F1: a single-duplex ~63 bp wireframe edge bends ~38 deg RMS (FLOPPY). The
    mechanics model maps (edge_bp, n_helices) -> persistence length -> RMS bend, anchored
    to the literature (single duplex Lp~50 nm; 6HB Lp~5 um measured by Kauert 2011)."""

    def test_mechanics_monotonic_in_helix_count(self):
        """More helices => stiffer bundle (higher EI/Lp) and lower RMS bend, strictly,
        and the single duplex (n=1) reduces exactly to the existing WLC function."""
        from molsynth import mechanics as mech
        # n=1 must equal the pre-existing single-duplex WLC bend exactly (no regression)
        self.assertAlmostEqual(mech.edge_rms_bend_deg(63, 1), seq.wlc_rms_bend_deg(63), places=9)
        self.assertEqual(mech.bundle_ei_ratio(1), 1.0)
        prev_bend, prev_ei, prev_lp = float("inf"), 0.0, 0.0
        for n in (1, 2, 3, 4, 6, 8):
            v = mech.stiffness_verdict(63, n)
            self.assertLess(v["rms_bend_deg"], prev_bend, f"bend not decreasing at n={n}")
            self.assertGreater(v["ei_ratio"], prev_ei, f"EI not increasing at n={n}")
            self.assertGreater(v["lp_bp"], prev_lp, f"Lp not increasing at n={n}")
            prev_bend, prev_ei, prev_lp = v["rms_bend_deg"], v["ei_ratio"], v["lp_bp"]

    def test_six_helix_bundle_lp_matches_literature(self):
        """The 6HB persistence length must land in the MEASURED 1-10 um range (Kauert 2011
        ~5 um; Bai 2012; Dietz 2009) -- the calibration anchor, not a free fit."""
        from molsynth import mechanics as mech
        lp_um = mech.bundle_lp_nm(6) / 1000.0
        self.assertTrue(1.0 <= lp_um <= 10.0, f"6HB Lp {lp_um:.2f} um outside literature 1-10 um")

    def test_single_duplex_floppy_bundle_rigid(self):
        """The core jump: a single-duplex ~63 bp edge is FLOPPY (>25 deg), a 6-helix bundle
        of the SAME edge is rigid (<=10 deg)."""
        from molsynth import mechanics as mech
        self.assertGreater(mech.edge_rms_bend_deg(63, 1), 25.0)        # floppy
        self.assertLessEqual(mech.edge_rms_bend_deg(63, 6), 10.0)      # rigid

    def test_compile_reports_floppy_by_default_rigid_with_bundle(self):
        """End-to-end: compile_shape default (edge_helices=1) reports a FLOPPY edge-stiffness
        verdict; edge_helices=6 reports a rigid (low-bend) verdict for the SAME shape."""
        from molsynth import compile_shape
        with tempfile.TemporaryDirectory() as d:
            s1 = compile_shape("tetrahedron", outdir=d, iterations=300,
                               scaffold_search=1, edge_helices=1)
            txt1 = open(os.path.join(d, "diagnostics.md"), encoding="utf-8").read()
        with tempfile.TemporaryDirectory() as d:
            s6 = compile_shape("tetrahedron", outdir=d, iterations=300,
                               scaffold_search=1, edge_helices=6)
            txt6 = open(os.path.join(d, "diagnostics.md"), encoding="utf-8").read()
        self.assertEqual(s1["edge_helices"], 1)
        self.assertEqual(s6["edge_helices"], 6)
        # default edge is floppy; the bundle edge is rigid (same geometry, only the dial moved)
        self.assertIn("FLOPPY", txt1)
        self.assertIn("edge_helices=6", txt6)
        self.assertIn("holds its designed shape", txt6)   # rigid-only verdict token (not bare "rigid")
        self.assertNotIn("FLOPPY", txt6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
