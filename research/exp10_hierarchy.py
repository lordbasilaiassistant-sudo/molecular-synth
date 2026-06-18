"""
Experiment 10 — hierarchy: compose the scales (origami unit cell -> super-lattice -> object).

Exp 2/5 settled the honest answer to "build a molecule, but bigger": you do NOT inflate one
molecule, you COMPOSE scales — hierarchical self-assembly. This experiment makes that ladder
quantitative for THIS repo's output: take the cube origami the compiler folds (~40 nm), let it
tile a 3D lattice via sticky-end handles, and recurse the lattice as a new unit cell across M
levels. At each level we ask the two physics questions that decide whether the rung self-builds:

  1. GRAVITY vs THERMAL — does the assembled block still shuffle itself by Brownian motion, or
     has it grown heavy enough that it just falls and sits? (reuse exp2's kT/(rho g) crossover.)
  2. BINDING vs THERMAL — does the handle valence holding a unit into the lattice survive thermal
     noise (multi-kT), so the super-assembly is stable? More handles per interface = more stable.

The walk shows exactly WHERE self-assembly stops carrying you up (the exp2 sweet spot,
~10 nm .. ~0.8 um) and you must switch mechanism (gel/template/active placement). That boundary
is a measured number, not a wall — it is the hand-off point between rungs of the-ladder.md.

Run:  python research/exp10_hierarchy.py
Pure stdlib (constants + the exp2 physics form). Self-checks at the bottom.
"""
from __future__ import annotations

import math

# --- physics constants (identical to exp2/exp5, so the crossover is the SAME number) ---
kB    = 1.380649e-23     # J/K
T     = 300.0            # K (room temp)
kT    = kB * T           # ~4.14e-21 J  -- the thermal-energy quantum
g     = 9.81             # m/s^2
rho   = 1100.0           # kg/m^3 (DNA/protein/water-ish; origami lattice is mostly solvent+DNA)
eta   = 1.0e-3           # Pa.s (water) -- Brownian timescale

# --- assembly / handle model ---
UNIT_NM     = 40.0       # one cube-origami unit cell ~ 40 nm edge (this repo's output scale)
N_PER_EDGE  = 4          # units per edge added at each hierarchy level (4^3 = 64 units/level block)
# A sticky-end handle is a short DNA duplex hybridisation. ~8 bp toehold/sticky end, and DNA
# duplex formation is ~ -1.5 kcal/mol per bp of NN free energy => one 8-bp handle ~ 12 kcal/mol.
# 1 kcal/mol = 6.9477e-21 J ~ 1.68 kT at 300 K. We model the PER-HANDLE binding free energy
# conservatively as the toehold's net stabilisation, ~ a few kT per handle (after entropy cost).
KCAL_PER_MOL_J = 6.9477e-21          # J per (kcal/mol) per molecule
HANDLE_BP      = 8                   # bases in one sticky-end handle
DG_PER_BP_KCAL = 1.5                 # |NN free energy| per bp (kcal/mol), SantaLucia-ish
# net per-handle free energy (computed in handle_dg_kT below) is the toehold's stabilisation
# minus the ~ +5 kcal/mol nucleation/entropy penalty for bringing two strands together
# (SantaLucia 1998 initiation term ~ +1.9, plus translational/rotational entropy).


def grav_thermal_crossover():
    """L where gravity (rho g L^4) == thermal (kT). Identical closed form to exp2."""
    return (kT / (rho * g)) ** 0.25


def grav_over_thermal(L):
    """E_grav/kT for a solid-ish block of linear size L (>1 => sediments, < => Brownian)."""
    return (rho * L ** 3) * g * L / kT


def diffuse_per_s(L):
    """rms Brownian displacement in 1 s for a sphere of size L (m). Stokes-Einstein."""
    D = kT / (6 * math.pi * eta * (L / 2))
    return math.sqrt(2 * D * 1.0)


def handle_dg_kT(handle_bp):
    """Per-handle binding free energy (kT) for a sticky end of `handle_bp` bases, net of the
    ~+5 kcal/mol nucleation/entropy penalty for bringing two strands together (SantaLucia 1998)."""
    dg_kcal = handle_bp * DG_PER_BP_KCAL - 5.0
    return dg_kcal * KCAL_PER_MOL_J / kT


def interface_binding_kT(handles_per_interface, handle_bp=HANDLE_BP):
    """Total binding free energy (in kT) holding one unit cell onto a neighbour via its handles.
    Monotonic in handle count by construction: each handle adds handle_dg_kT of stabilisation.
    >~ a few kT => the bond beats thermal noise and the super-assembly is stable."""
    return handles_per_interface * handle_dg_kT(handle_bp)


def level_size_nm(level):
    """Linear size of the assembled block after `level` hierarchy levels.
    level 0 = the bare unit cell; each level multiplies the edge by N_PER_EDGE."""
    return UNIT_NM * (N_PER_EDGE ** level)


def n_units(level):
    """Total origami unit cells in the level-`level` block (a few levels is astronomical)."""
    return (N_PER_EDGE ** level) ** 3


def fmt_units(n):
    """Compact count: exact with thousands separators up to ~1e6, else scientific."""
    return f"{n:,}" if n < 1_000_000 else f"{n:.2e}"


def fmt_len(nm):
    if nm < 1e3:
        return f"{nm:.0f} nm"
    if nm < 1e6:
        um = nm / 1e3
        return f"{um:.1f} um" if um < 10 else f"{um:.0f} um"
    return f"{nm/1e6:.2f} mm"


def main():
    L_gt = grav_thermal_crossover()
    # exp2's manipulation/self-assembly sweet spot ceiling is the gravity=thermal crossover;
    # floor (one interface = 1 kT) is ~0.5 nm, robust-multi-kT by ~10 nm.
    sweet_lo_nm, sweet_hi_nm = 10.0, L_gt * 1e9
    handles = 4   # handles per inter-unit interface for the size ladder (one valence choice)

    dg8_kcal = HANDLE_BP * DG_PER_BP_KCAL - 5.0
    print(f"kT(300K)={kT:.2e} J   rho={rho:.0f} kg/m^3   unit cell={UNIT_NM:.0f} nm   "
          f"branch={N_PER_EDGE}/edge")
    print(f"per-handle binding ~ {dg8_kcal:.1f} kcal/mol = {handle_dg_kT(HANDLE_BP):.2f} kT "
          f"({HANDLE_BP}-bp sticky end, net of entropy)\n")
    print("SELF-ASSEMBLY LADDER  (cube origami -> super-lattice, {} handles/interface):".format(handles))
    print(f"{'level':>5}{'units':>16}{'size':>10}{'grav/kT':>12}{'diffuse/s':>12}"
          f"{'bind/kT':>10}  regime")
    print("-" * 88)
    last_in = None
    crossover_level = None
    for lvl in range(0, 7):
        L_nm = level_size_nm(lvl)
        L_m = L_nm * 1e-9
        gt = grav_over_thermal(L_m)
        dx = diffuse_per_s(L_m)
        bind = interface_binding_kT(handles)
        in_sweet = sweet_lo_nm <= L_nm <= sweet_hi_nm
        if last_in is True and in_sweet is False and crossover_level is None:
            crossover_level = lvl
        last_in = in_sweet
        dxs = (f"{dx*1e9:.0f} nm/s" if dx < 1e-6 else
               f"{dx*1e6:.2g} um/s" if dx < 1e-3 else
               f"{dx*1e3:.2g} mm/s")
        regime = "self-assembles" if in_sweet else "TOO HEAVY -> falls/sits (need new mechanism)"
        if gt < 1 and not in_sweet:
            regime = "Brownian but sub-10nm (too small to hold shape)"
        print(f"{lvl:>5}{fmt_units(n_units(lvl)):>16}{fmt_len(L_nm):>10}{gt:>12.2e}{dxs:>12}"
              f"{bind:>10.1f}  {regime}")

    print(f"\nGRAVITY = THERMAL crossover at L ~ {L_gt*1e9:.0f} nm = {L_gt*1e6:.2f} um  "
          f"(exp2's ~0.79 um sweet-spot ceiling)")
    if crossover_level is not None:
        prev = fmt_len(level_size_nm(crossover_level - 1))
        now = fmt_len(level_size_nm(crossover_level))
        print(f"  -> self-assembly carries you to ~level {crossover_level-1} ({prev}); at level "
              f"{crossover_level} ({now}) gravity wins and Brownian assembly STOPS.")
    print("  Above the ceiling you must hand off to another rung of the-ladder.md: silica/metal")
    print("  hardening (rung 1), templated placement, or active (energy-burning) assembly.\n")

    # --- BINDING vs kT: stability is monotonic in handle valence (the design knob) ---
    # Two handle lengths show valence is a REAL lever: a weak 4-bp toehold per handle needs
    # several handles to clear the multi-kT stability bar, an 8-bp handle is robust almost alone.
    print("HANDLE VALENCE vs STABILITY  (binding free energy per interface, must be >> 1 kT):")
    print(f"{'handles':>8}{'4-bp bind/kT':>14}{'8-bp bind/kT':>14}  verdict (8-bp)")
    print("-" * 56)
    prev4, prev8 = -1.0, -1.0
    monotonic = True
    for h in (1, 2, 4, 6, 8, 12):
        b4 = interface_binding_kT(h, handle_bp=4)
        b8 = interface_binding_kT(h, handle_bp=8)
        if b4 <= prev4 or b8 <= prev8:
            monotonic = False
        prev4, prev8 = b4, b8
        verdict = ("falls apart (<3 kT)" if b8 < 3 else
                   "marginal (3-8 kT)" if b8 < 8 else
                   "robust super-assembly")
        print(f"{h:>8}{b4:>14.1f}{b8:>14.1f}  {verdict}")
    print(f"\n  binding-vs-kT is monotonic in handle count for both handle lengths: {monotonic}")
    print(f"  (more handles per interface = strictly more stable; one 4-bp handle ~"
          f"{handle_dg_kT(4):.1f} kT, one 8-bp ~{handle_dg_kT(8):.1f} kT).")
    print("  This is the bottom-rung design lever: program valence + handle length to clear the")
    print("  multi-kT bar, and hierarchy self-assembles the lattice up to the gravity ceiling.")

    print("\nHONEST READ: origami (~40 nm) sits squarely in the exp2 sweet spot; a few levels of")
    print("handle-driven tiling reach ~um blocks that STILL self-assemble. Past ~0.8 um the same")
    print("trillion-fold Brownian search that built the bottom rung dies -- you don't inflate the")
    print("molecule, you compose scales and SWITCH MECHANISM at the measured crossover. That is")
    print("the molecule->macro path, one demonstrated rung at a time (the-ladder.md).")


def _self_check():
    """Lightweight measured assertions (also the test, runnable directly)."""
    # 1) the gravity=thermal crossover MUST match exp2's ~0.79 um (same constants, same form).
    L_gt_um = grav_thermal_crossover() * 1e6
    assert abs(L_gt_um - 0.79) < 0.05, f"crossover {L_gt_um:.3f} um != exp2's ~0.79 um"

    # 2) binding-vs-kT stability is strictly monotonic increasing in handle count, for both a
    #    weak 4-bp toehold and the standard 8-bp sticky end.
    for bp in (4, 8):
        binds = [interface_binding_kT(h, handle_bp=bp) for h in range(1, 13)]
        assert all(b2 > b1 for b1, b2 in zip(binds, binds[1:])), \
            f"binding not monotonic in handles at {bp} bp"
        assert binds[0] > 0, f"a single {bp}-bp handle must give positive binding free energy"

    # 3) the bottom rung (40 nm origami) is inside exp2's self-assembly sweet spot; some level
    #    above the gravity crossover is NOT (self-assembly provably stops climbing).
    assert grav_over_thermal(UNIT_NM * 1e-9) < 1.0, "unit cell should be Brownian"
    big = level_size_nm(6) * 1e-9
    assert grav_over_thermal(big) > 1.0, "top level should be gravity-dominated (assembly stops)"

    # 4) per-handle binding is a few-to-~12 kT (sane sticky-end energetics): a 4-bp toehold is
    #    weak (~1-3 kT, valence-limited) while an 8-bp handle is already multi-kT on its own.
    assert 0.5 < handle_dg_kT(4) < 4.0, f"4-bp handle {handle_dg_kT(4):.2f} kT out of sane range"
    assert 8.0 < handle_dg_kT(8) < 15.0, f"8-bp handle {handle_dg_kT(8):.2f} kT out of sane range"
    assert interface_binding_kT(8, handle_bp=8) > 8.0, "8x8-bp handles should be a robust bond"
    print("exp10 self-check OK: crossover ~0.79 um matches exp2; binding monotonic in handles.")


if __name__ == "__main__":
    main()
    print()
    _self_check()
