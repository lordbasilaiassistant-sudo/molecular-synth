"""
Experiment 2 — "What if we built molecules, but bigger?"  The physics of scale.

A creative prompt (drlor): the universe feels recursively self-similar — zoom in or out and
patterns repeat — so could we reconstruct a molecule at a size we can actually grab, and make,
say, giant food?

This experiment answers it with numbers instead of hand-waving. The honest physics has two
halves, and BOTH are true:

  1. STRUCTURE can be self-similar across scale (fractals, critical phenomena, turbulent
     cascades, the renormalization group). The intuition "patterns repeat up/down" is real.

  2. FORCES are NOT scale-invariant. The dimensionless ratios (surface/volume, gravity/thermal,
     binding/thermal, Reynolds number) change with linear size L, so a DIFFERENT force
     dominates at each scale. That is why you cannot just "scale a molecule up": a chemical
     bond IS its length (~0.15 nm of quantum overlap); a 10 cm "C-C bond" is not a stronger
     bond, it is two atoms doing nothing.

We sweep object size L over ~10 orders of magnitude and compute, per object, the competing
energies that decide its behavior. The crossover scales reveal a genuine MANIPULATION /
SELF-ASSEMBLY SWEET SPOT — and it is exactly where DNA origami (this repo) operates.

Run:  python research/exp2_scale_physics.py
Pure stdlib (constants only).
"""
from __future__ import annotations

import math

kB   = 1.380649e-23     # J/K
T    = 300.0            # K (room temp)
kT   = kB * T           # ~4.14e-21 J  -- the thermal energy quantum (drives Brownian motion)
g    = 9.81             # m/s^2
rho  = 1100.0           # kg/m^3 (DNA/protein/food ~ water-ish)
# base-stacking / H-bond "molecular glue": ~1.5 kcal/mol per bp interface ~ 1e-20 J,
# i.e. an interfacial binding-energy density. DNA duplex ~0.34 nm/bp over ~2 nm width:
sigma_bind = 0.02       # J/m^2  (vdW/stacking interfacial energy density, ~20 mJ/m^2)
eta  = 1.0e-3           # Pa.s (water) -- for the diffusion/Brownian timescale

SCALES = [
    ("C-C bond",        0.15e-9),
    ("glucose",         0.5e-9),
    ("protein",         5e-9),
    ("DNA origami",     50e-9),
    ("virus / origami", 100e-9),
    ("large origami",   1e-6),
    ("bacterium",       2e-6),
    ("red blood cell",  8e-6),
    ("dust / pollen",   50e-6),
    ("grain of salt",   0.5e-3),
    ("pea",             1e-2),
    ("apple",           7e-2),
    ("human",           1.7e0),
]


def report(L):
    """Competing energies/ratios for a solid sphere-ish object of linear size L."""
    m      = rho * L ** 3                     # mass (kg), volume ~ L^3
    E_grav = m * g * L                        # work to lift it its own height ~ rho g L^4
    E_bind = sigma_bind * L ** 2              # interfacial binding holding two halves ~ L^2
    sv     = 1.0 / L                          # surface/volume ratio (1/m); surface forces ~ 1/L
    # Brownian: rms displacement per second; D = kT/(6 pi eta r), r=L/2
    D      = kT / (6 * math.pi * eta * (L / 2))
    x_rms  = math.sqrt(2 * D * 1.0)           # rms diffusion in 1 s (m)
    return {
        "grav_over_thermal": E_grav / kT,     # >1 => gravity/sedimentation beats Brownian
        "bind_over_thermal": E_bind / kT,     # >>1 => a glued interface survives thermal noise
        "surf_vol": sv,                        # high => surface (adhesion/vdW) world
        "diffuse_1s": x_rms,                   # how far thermal motion carries it per second
    }


def main():
    print(f"kT (300 K) = {kT:.2e} J   rho = {rho:.0f} kg/m^3   sigma_bind = {sigma_bind*1000:.0f} mJ/m^2\n")
    print(f"{'object':18}{'L':>10}{'grav/kT':>14}{'bind/kT':>12}{'S/V (1/m)':>12}{'diffuse/s':>12}")
    print("-" * 78)
    for name, L in SCALES:
        r = report(L)
        # human-friendly diffusion
        dx = r["diffuse_1s"]
        dxs = (f"{dx*1e9:.0f} nm/s" if dx < 1e-6 else
               f"{dx*1e6:.1f} um/s" if dx < 1e-3 else
               f"{dx*1e3:.2f} mm/s" if dx < 1 else f"{dx:.1e} m/s")
        Ls = (f"{L*1e9:.2g} nm" if L < 1e-6 else
              f"{L*1e6:.2g} um" if L < 1e-3 else
              f"{L*1e3:.2g} mm" if L < 1 else f"{L:.2g} m")
        print(f"{name:18}{Ls:>10}{r['grav_over_thermal']:>14.2e}"
              f"{r['bind_over_thermal']:>12.1e}{r['surf_vol']:>12.1e}{dxs:>12}")

    # crossover scales (closed form)
    L_grav = (kT / (rho * g)) ** 0.25         # gravity == thermal  -> sedimentation begins
    L_bind = (kT / sigma_bind) ** 0.5         # one interface == one kT -> assembly barely holds
    print("\nCROSSOVERS")
    print(f"  gravity = thermal at  L ~ {L_grav*1e6:.2f} um   "
          "(below: Brownian/colloidal world; above: it just falls/sits)")
    print(f"  bind   = 1 kT   at    L ~ {L_bind*1e9:.2f} nm   "
          "(above: a glued face beats thermal noise -> self-assembly is stable)")
    print("\nSWEET SPOT (programmable matter you can build by the trillions AND hold a shape):")
    print(f"  floor ~{L_bind*1e9:.1f} nm (one interface = 1 kT); robust multi-kT assemblies by ~10 nm.")
    print(f"  ceiling ~{L_grav*1e6:.1f} um (gravity takes over). Practical window ~10 nm .. ~0.8 um")
    print("  <-- exactly the DNA-origami window (10 nm - 1 um) this repo compiles.")
    print("\nWHY NOT 'just scale a molecule up':")
    print("  A bond is ~0.15 nm of quantum orbital overlap; stretch it and it is no longer a")
    print("  bond. Properties (color, taste, stiffness, melting) ARE emergent at their scale.")
    print("  The real path molecule->macroscopic is HIERARCHICAL self-assembly (glucose ->")
    print("  cellulose -> cell wall -> lettuce), which nature already runs for food. Our")
    print("  buildable lever is to PROGRAM the bottom rung (origami) and let hierarchy do the")
    print("  rest -- not to inflate a single molecule.")


if __name__ == "__main__":
    main()
