"""Tests for the Drink Synth request-compiler. Run: python synth/tests/test_drinksynth.py"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "synth"))

from drinksynth import compile_drink, parse           # noqa: E402
from drinksynth import recipes as R                    # noqa: E402


class TestDrinkSynth(unittest.TestCase):
    def test_iced_sets_chill_and_ice(self):
        d = parse("iced latte")
        self.assertTrue(d.iced)
        self.assertEqual(d.target_c, R.ICED_C)
        cmds = compile_drink("iced latte")["commands"]
        self.assertTrue(any(c.startswith("ICE") for c in cmds))
        self.assertIn("TEMP 4", cmds[0])

    def test_hot_is_not_iced(self):
        d = parse("hot americano")
        self.assertFalse(d.iced)
        self.assertEqual(d.target_c, R.HOT_C)

    def test_extra_shot_adds_coffee(self):
        base = parse("latte").ingredients.get("coffee", 0)
        more = parse("latte, extra shot").ingredients.get("coffee", 0)
        self.assertEqual(more, base + 30)

    def test_oat_substitutes_dairy(self):
        d = parse("oat latte")
        self.assertIn("oat_milk", d.ingredients)
        self.assertNotIn("dairy_milk", d.ingredients)

    def test_size_scaling(self):
        small = parse("coffee, small").size_ml
        large = parse("coffee, large").size_ml
        self.assertLess(small, large)

    def test_commands_pump_ids_valid(self):
        cmds = compile_drink("iced oat latte, large, extra shot")["commands"]
        pumps = [c for c in cmds if c.startswith("PUMP")]
        self.assertTrue(pumps)
        for c in pumps:
            pid = int(c.split()[1])
            self.assertIn(pid, [v["pump"] for v in R.PUMPS.values()])
        self.assertEqual(cmds[-1], "DONE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
