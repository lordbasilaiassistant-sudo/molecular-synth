"""Tests for the Water Synth request-compiler. Run: python synth/tests/test_watersynth.py"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "synth"))

from watersynth import compile_water, parse        # noqa: E402


class TestWaterSynth(unittest.TestCase):
    def test_cold_sets_low_temp(self):
        self.assertLessEqual(parse("cold water").temp_c, 4)

    def test_hot_sets_high_temp(self):
        self.assertGreaterEqual(parse("hot water").temp_c, 80)

    def test_large_scales_volume(self):
        self.assertGreater(parse("large glass of water").volume_ml,
                           parse("water").volume_ml)

    def test_harvest_then_treat_then_dispense(self):
        cmds = compile_water("cold water")["commands"]
        kinds = [c.split()[0] for c in cmds]
        self.assertEqual(kinds[0], "HARVEST")
        self.assertIn("UV", kinds)
        self.assertIn("DISPENSE", kinds)
        self.assertEqual(kinds[-1], "DONE")

    def test_reservoir_skips_harvest(self):
        cmds = compile_water("water", from_reservoir=True)["commands"]
        self.assertFalse(any(c.startswith("HARVEST") for c in cmds))

    def test_honest_scope_stamped(self):
        self.assertIn("NOT synthesised from energy",
                      compile_water("water")["protocol"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
