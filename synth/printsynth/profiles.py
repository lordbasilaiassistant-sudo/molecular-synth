"""
Print profiles for the 3D-print maker.

Honest scope: printsynth orchestrates a standard FDM 3D printer — it takes a mesh (STL)
and emits a print JOB (material, settings, time + filament estimate, and the slicer
hand-off). It does not reinvent slicing; a free slicer (PrusaSlicer / Cura) generates the
gcode. The printer + filament are cheap, orderable parts (a real maker), so "a printed
object" becomes something the system makes — form in plastic, not functional electronics.
"""

from __future__ import annotations

# filament density g/cm^3, nozzle/bed temps, typical throughput g/hr on a 0.4 mm nozzle
MATERIALS = {
    "PLA":  {"density": 1.24, "nozzle_C": 205, "bed_C": 60,  "g_per_hr": 14},
    "PETG": {"density": 1.27, "nozzle_C": 240, "bed_C": 80,  "g_per_hr": 12},
    "ABS":  {"density": 1.04, "nozzle_C": 245, "bed_C": 100, "g_per_hr": 12},
    "TPU":  {"density": 1.21, "nozzle_C": 225, "bed_C": 50,  "g_per_hr": 6},
}
DEFAULT_MATERIAL = "PLA"

# generic hobbyist FDM printer (Ender-3 class) — orderable ~$150-250
PRINTER = {"name": "generic FDM (Ender-3 class)", "build_mm": (220, 220, 250), "nozzle_mm": 0.4}

DEFAULT_LAYER_MM = 0.2
DEFAULT_INFILL = 0.20      # 20%
WALL_FRACTION = 0.18       # rough solid-fraction added by perimeters/top/bottom
PRICE_PER_KG = 22.0        # USD, typical PLA spool
