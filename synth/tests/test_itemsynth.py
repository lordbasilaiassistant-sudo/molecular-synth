"""Tests for the Item Synth request-router (the maker-federation front door).
Run: python synth/tests/test_itemsynth.py
"""
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "synth"))
sys.path.insert(0, os.path.join(ROOT, "compiler"))

from itemsynth import classify, route        # noqa: E402


class TestClassify(unittest.TestCase):
    def test_each_domain_routes(self):
        cases = {
            "a large glass of cold water": "water",
            "iced oat latte, large": "drink",
            "hot americano": "drink",
            "print me a bracket": "print",
            "a DNA octahedron nanocage": "molecular",
            "an origami tetrahedron": "molecular",
        }
        for req, want in cases.items():
            self.assertEqual(classify(req)["domain"], want, req)

    def test_print_intent_beats_device_noun(self):
        # "phone case" / "cell phone case" are PRINT jobs, not impossible electronics
        self.assertEqual(classify("a phone case")["domain"], "print")
        self.assertEqual(classify("a cell phone case")["domain"], "print")

    def test_impossible_routes_to_north_star(self):
        for req in ("a working smartphone", "a laptop", "replicate matter from atoms",
                    "make me a cpu", "a steak from atoms"):
            self.assertEqual(classify(req)["domain"], "north-star", req)

    def test_glass_of_water_is_water_not_drink(self):
        c = classify("a glass of water")
        self.assertEqual(c["domain"], "water")

    def test_unknown_when_nothing_matches(self):
        self.assertEqual(classify("something nice please")["domain"], "unknown")

    def test_decision_is_auditable(self):
        c = classify("iced matcha latte")
        self.assertGreater(c["confidence"], 0)
        self.assertTrue(c["matched"])          # the terms that drove the decision


class TestRoute(unittest.TestCase):
    def test_water_dispatch(self):
        r = route("cold water")
        self.assertEqual(r["maker"], "water")
        self.assertTrue(any(cmd.startswith("DISPENSE") for cmd in r["recipe"]))

    def test_drink_dispatch(self):
        r = route("hot americano")
        self.assertEqual(r["maker"], "drink")
        self.assertIn("DONE", r["recipe"])

    def test_print_dispatch(self):
        r = route("a small bracket")
        self.assertEqual(r["maker"], "print")
        self.assertTrue(any("MATERIAL" in c for c in r["recipe"]))

    def test_print_uses_real_stl_when_named(self):
        stl = os.path.join(ROOT, "examples", "octahedron.stl")
        if not os.path.exists(stl):
            self.skipTest("octahedron.stl not present")
        r = route(f"3d print {stl}")
        self.assertEqual(r["maker"], "print")
        self.assertIn("measured from", r["honest_note"])     # exact metrics, not the estimate

    def test_north_star_is_not_faked(self):
        r = route("a working smartphone")
        self.assertIsNone(r["maker"])
        self.assertIsNone(r["recipe"])
        self.assertIn("north-star", r["honest_note"])

    def test_unknown_asks_for_specifics(self):
        r = route("hmm")
        self.assertIsNone(r["maker"])
        self.assertIn("Couldn't tell", r["ticket"])

    def test_molecular_classify_only_skips_heavy_compile(self):
        r = route("a DNA tetrahedron", compile_molecular=False)
        self.assertEqual(r["maker"], "molecular")
        self.assertEqual(r["shape"], "tetrahedron")
        self.assertIsNone(r["recipe"])

    def test_molecular_full_compile_emits_design(self):
        with tempfile.TemporaryDirectory() as d:
            r = route("an octahedron nanostructure", outdir=d)
            self.assertEqual(r["maker"], "molecular")
            self.assertEqual(r["shape"], "octahedron")
            # the real maker wrote orderable + foldable artifacts
            for f in ("scaffold.fasta", "staples.csv", "protocol.md"):
                self.assertTrue(os.path.exists(os.path.join(d, f)), f)


if __name__ == "__main__":
    unittest.main(verbosity=2)
