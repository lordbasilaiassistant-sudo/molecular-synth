"""Tests for the Maker Catalog. Run: python catalog/tests/test_makerlib.py"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "catalog"))

from makerlib import check, list_catalog, load_catalog          # noqa: E402
from makerlib import order, interpret                            # noqa: E402
from makerlib.checker import FEASIBILITY_ORDER, best_feasibility  # noqa: E402


class TestMakerlib(unittest.TestCase):
    def test_catalog_schema_valid(self):
        cat = load_catalog()
        self.assertIn("items", cat)
        for it in cat["items"]:
            self.assertIn("name", it)
            self.assertTrue(it.get("decomposition"))
            self.assertTrue(it.get("styles"))
            for s in it["styles"]:
                self.assertIn(s["feasibility"], FEASIBILITY_ORDER, it["name"])
                self.assertIn("maker", s)

    def test_water_has_two_styles_same_system(self):
        r = check("glass of water")
        self.assertEqual(r["best_feasibility"], "ready")
        makers = {s["maker"] for s in r["styles"]}
        self.assertEqual(makers, {"watersynth"})       # same system
        self.assertGreaterEqual(len(r["styles"]), 2)   # different styles

    def test_cookie_decomposes_to_molecules(self):
        r = check("cookie")
        self.assertEqual(r["best_feasibility"], "assemble")
        joined = " ".join(r["decomposition"]).lower()
        self.assertIn("flour", joined)
        self.assertTrue("molecule" in joined or "sucrose" in joined or "protein" in joined)

    def test_phone_is_north_star(self):
        self.assertEqual(check("working phone")["best_feasibility"], "north-star")

    def test_unknown_food_estimated(self):
        r = check("lasagna")           # not cataloged
        self.assertFalse(r["cataloged"])
        self.assertEqual(r["best_feasibility"], "assemble")

    def test_best_feasibility_picks_most_ready(self):
        styles = [{"feasibility": "frontier"}, {"feasibility": "ready"}]
        self.assertEqual(best_feasibility(styles), "ready")

    def test_alias_lookup(self):
        self.assertEqual(check("h2o")["name"], "water")
        self.assertEqual(check("iced latte")["name"], "latte")


class TestOrderBrain(unittest.TestCase):
    def test_whiskey_on_the_rocks_is_ice_plus_whiskey(self):
        i = interpret("whiskey on the rocks")
        self.assertEqual(i["kind"], "drink")
        self.assertTrue(i["ice"])
        self.assertIn("whiskey", i["pour"])
        plan = order("whiskey on the rocks")
        self.assertEqual(set(plan["makers"]), {"watersynth", "drinksynth"})  # cross-maker
        self.assertIn("ICE 80", plan["machine_commands"])

    def test_neat_has_no_ice(self):
        self.assertFalse(interpret("whiskey neat")["ice"])

    def test_double_scales_the_spirit(self):
        base = interpret("whiskey on the rocks")["pour"]["whiskey"]
        dbl = interpret("double whiskey on the rocks")["pour"]["whiskey"]
        self.assertEqual(dbl, base * 2)

    def test_alias_and_mixer(self):
        i = interpret("g&t")
        self.assertEqual(i["name"], "gin and tonic")
        self.assertIn("tonic water", i["pour"])
        self.assertTrue(i["ice"])

    def test_non_drink_falls_back_to_catalog(self):
        self.assertEqual(interpret("cookie")["kind"], "catalog")
        self.assertEqual(order("cookie")["feasibility"], "assemble")

    def test_llm_hook_used_when_provided(self):
        # an "AI" that rewrites slang to a known phrase
        plan = order("gimme the usual", llm=lambda t: "whiskey on the rocks")
        self.assertEqual(set(plan["makers"]), {"watersynth", "drinksynth"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
