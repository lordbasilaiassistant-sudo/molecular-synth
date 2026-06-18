"""
Experiment 5 — WHY does size matter, and can we "have it all ways"?

drlor's push: "why does size matter so much? why can't we have it all ways? I doubt it's a
hard wall — we're missing something." Both halves are addressable with numbers.

THE ROOT CAUSE (not a wall — geometry of exponents):
  Every force is SOURCED by a different-dimensional feature of an object, so each scales as a
  different POWER of linear size L:
      thermal energy  kT          ~ L^0   (constant! one bond feels ~kT whatever its host's size)
      surface forces  (vdW,       ~ L^2   (act across interfaces -> area)
                       adhesion,
                       drag, tension)
      body forces     (gravity,   ~ L^3   (sourced by amount of stuff -> volume; weight)
                       inertia)
  A "crossover scale" is just where two lines of DIFFERENT SLOPE cross on a log-log plot.
  Size matters because moving away from the atomic scale changes the COUNT of fundamental
  units involved (N atoms, N bonds, area, volume) and each force cares about a different count.
  You can't have it all ways in ONE monolithic object because it has ONE size, which already
  fixed the L^3-vs-L^2-vs-L^0 winner.

THE BEDROCK YOU CANNOT DODGE:
  The atomic scale is PINNED by the fundamental constants. The Bohr radius
  a0 = hbar^2/(m_e e^2) ~ 0.053 nm is a fixed combination of constants of the universe.
  Bond length ~0.15 nm, bond energy ~eV, kT ~ 1/40 eV are all set there. You cannot make a
  "bigger atom." That single pinned scale + a scale-free kT is the whole origin of scale.

THE DODGE (where drlor is RIGHT — we ARE missing it if we think monolithic):
  Nature never accepts the 1/L surface penalty. It makes surface FRACTAL/hierarchical so
  effective area ~ L^D with 2 < D < 3, decoupling area from the naive L^2. Lungs, guts,
  mitochondria, nacre, bone, wood: multi-scale structure has molecular chemistry AND macro
  size AT ONCE. You don't beat the scaling laws — you COMPOSE them across scales (and spend
  structural complexity + energy to do it). That is the real road to "giant" anything.

Run:  python research/exp5_why_scale_matters.py
Pure stdlib.
"""
from __future__ import annotations

import math

kB, T, g = 1.380649e-23, 300.0, 9.81
kT = kB * T
rho, sigma = 1100.0, 0.02            # kg/m^3, J/m^2  (as in exp2)
hbar, m_e, e, eps0 = 1.054571817e-34, 9.1093837e-31, 1.602176634e-19, 8.8541878128e-12


def slope(f, L0=1e-9, L1=1e-3):
    """Empirical log-log slope (the exponent n in E ~ L^n) of a force/energy law."""
    return (math.log(f(L1)) - math.log(f(L0))) / (math.log(L1) - math.log(L0))


def main():
    # --- 1) the pinned scale: derive the Bohr radius from raw constants ---
    a0 = (4 * math.pi * eps0 * hbar ** 2) / (m_e * e ** 2)
    print("1) THE PINNED SCALE (cannot be dodged):")
    print(f"   Bohr radius a0 = hbar^2 4pi eps0 / (m_e e^2) = {a0*1e9:.4f} nm")
    print(f"   -> atoms, bonds (~0.15 nm), bond energy (~eV), and kT (~{kT/e:.3f} eV) are all")
    print("      set HERE by the universe's constants. There is no 'bigger atom'.\n")

    # --- 2) the exponents: why each force scales differently ---
    laws = {
        "thermal kT":          lambda L: kT,                 # L^0
        "surface (vdW/adhesion)": lambda L: sigma * L ** 2,  # L^2
        "gravity (weight*L)":  lambda L: rho * g * L ** 4,    # L^4 (lift weight by its own size)
        "diffusion reach/s":   lambda L: math.sqrt(2 * (kT / (6 * math.pi * 1e-3 * (L / 2))) * 1),  # ~L^-0.5
    }
    print("2) WHY SIZE MATTERS = forces are different POWERS of L (measured slopes):")
    for name, f in laws.items():
        print(f"   {name:26} exponent n = {slope(f):+.2f}   (E ~ L^{slope(f):.0f})")
    print("   -> 'crossovers' are just lines of different slope intersecting. Geometry, not a wall.")
    L_gt = (kT / (rho * g)) ** 0.25
    print(f"   gravity = thermal at L ~ {L_gt*1e6:.2f} um; below it thermal (L^0) towers over weight.\n")

    # --- 3) the dodge: fractal/hierarchical surface beats the 1/L penalty ---
    print("3) THE DODGE (have-it-more-ways): make area FRACTAL, A ~ L^D, 2<D<3.")
    L = 0.15                              # 15 cm, lung-ish linear size
    A_solid = 4 * math.pi * (L / 2) ** 2   # monolithic sphere surface (~L^2)
    # human lung: ~75 m^2 of gas-exchange surface in a ~0.15 m organ; airway tree D ~ 2.97
    A_lung = 75.0
    D = 2.0 + math.log(A_lung / A_solid) / math.log(L / 0.15e-3)   # effective fractal dim vs 0.15mm alveolus
    print(f"   solid 15 cm sphere surface : {A_solid:.3f} m^2")
    print(f"   human lung (same size)     : {A_lung:.0f} m^2   = {A_lung/A_solid:.0f}x more, eff. D~{min(D,3.0):.2f} (near space-filling)")
    print("   -> molecular-scale surface chemistry AND macroscopic size, simultaneously, by")
    print("      nesting structure across scales. Bone, wood, nacre, gut, mitochondria do this.")
    print("   You don't break the scaling laws; you COMPOSE them (cost: complexity + energy).\n")

    print("ANSWER: size matters because the constants pin ONE scale (atomic) and kT is scale-free,")
    print("so every force re-sorts by a different power of L as you move away. A monolithic object")
    print("can't 'have it all ways' -- it has one size. A MULTI-SCALE (hierarchical/active/structured)")
    print("object can have many ways at once. That -- not inflating a molecule -- is what we're missing,")
    print("and it's exactly the lever DNA origami opens at the bottom rung. (See docs/the-ladder.md.)")


if __name__ == "__main__":
    main()
