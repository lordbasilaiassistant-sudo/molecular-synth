"""Tests for the 3D-print maker. Run: python synth/tests/test_printsynth.py"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "synth"))

from printsynth import compile_print, mesh_metrics    # noqa: E402


class TestPrintSynth(unittest.TestCase):
    def test_estimate_scales_and_fits(self):
        j = compile_print(volume_cm3=20.0, bbox_mm=(40, 40, 40), material="PLA", infill=0.2)
        self.assertGreater(j["filament_g"], 0)
        self.assertGreater(j["time_h"], 0)
        self.assertGreater(j["cost_usd"], 0)
        self.assertTrue(j["fits"])
        self.assertEqual(j["material"], "PLA")
        self.assertEqual(j["commands"][0], "MATERIAL PLA")
        self.assertEqual(j["commands"][-1], "DONE")

    def test_infill_increases_filament(self):
        a = compile_print(volume_cm3=20.0, infill=0.1)["filament_g"]
        b = compile_print(volume_cm3=20.0, infill=0.5)["filament_g"]
        self.assertGreater(b, a)

    def test_oversize_flagged(self):
        j = compile_print(volume_cm3=10.0, bbox_mm=(300, 50, 50))   # >220 mm build
        self.assertFalse(j["fits"])

    def test_stl_parses(self):
        stl = os.path.join(ROOT, "examples", "octahedron.stl")
        if not os.path.exists(stl):
            self.skipTest("octahedron.stl not generated")
        j = compile_print(stl=stl)
        self.assertEqual(len(j["bbox_mm"]), 3)
        self.assertIn("prusa-slicer", j["slicer_cmd"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
