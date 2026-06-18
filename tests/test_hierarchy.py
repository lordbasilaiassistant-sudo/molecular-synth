"""
Focused test for research/exp10_hierarchy.py — the hierarchy (compose-the-scales) rung.
Stdlib unittest only (no pip deps). Run:

    python tests/test_hierarchy.py
    # or:  python -m pytest tests/

Asserts the cross-experiment invariant that makes exp10 honest: its gravity=thermal
self-assembly ceiling MUST equal exp2's closed-form crossover (same physics, same constants),
and super-assembly stability MUST be monotonic in handle valence.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "research"))

import exp2_scale_physics as exp2      # noqa: E402
import exp10_hierarchy as exp10        # noqa: E402


class TestHierarchy(unittest.TestCase):
    def test_crossover_matches_exp2(self):
        """exp10's self-assembly ceiling is exp2's gravity=thermal crossover (~0.79 um)."""
        exp10_um = exp10.grav_thermal_crossover() * 1e6
        # exp2 computes the same closed form inline: L_grav = (kT/(rho g))**0.25
        exp2_um = (exp2.kT / (exp2.rho * exp2.g)) ** 0.25 * 1e6
        self.assertAlmostEqual(exp10_um, exp2_um, places=9,
                               msg="exp10 ceiling must equal exp2's crossover exactly")
        self.assertAlmostEqual(exp10_um, 0.79, delta=0.05)

    def test_binding_monotonic_in_valence(self):
        """More handles per interface => strictly more binding free energy, for both lengths."""
        for bp in (4, 8):
            binds = [exp10.interface_binding_kT(h, handle_bp=bp) for h in range(1, 13)]
            self.assertTrue(all(b2 > b1 for b1, b2 in zip(binds, binds[1:])),
                            f"binding not monotonic at {bp} bp")
            self.assertGreater(binds[0], 0.0)

    def test_handle_energetics_sane(self):
        """Per-handle binding is physically sane: weak 4-bp toehold ~1-3 kT, 8-bp ~multi-kT."""
        self.assertTrue(0.5 < exp10.handle_dg_kT(4) < 4.0)
        self.assertTrue(8.0 < exp10.handle_dg_kT(8) < 15.0)

    def test_unit_cell_brownian_top_level_gravity(self):
        """40 nm origami self-assembles (Brownian); a high level is gravity-dominated."""
        self.assertLess(exp10.grav_over_thermal(exp10.UNIT_NM * 1e-9), 1.0)
        self.assertGreater(exp10.grav_over_thermal(exp10.level_size_nm(6) * 1e-9), 1.0)

    def test_self_check_runs(self):
        """The exp10 __main__ self-check assertions all pass."""
        exp10._self_check()


if __name__ == "__main__":
    unittest.main(verbosity=2)
