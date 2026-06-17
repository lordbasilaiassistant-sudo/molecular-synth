"""
Print Synth — the 3D-print maker. Mesh (STL) -> print job (material, settings, time +
filament + cost estimate, slicer hand-off). Adds physical OBJECTS to what the system
makes. Honest: a standard FDM printer + free slicer does the work; form in plastic only.

    from printsynth import compile_print
    job = compile_print("part.stl", material="PLA", infill=0.2)

CLI:  python -m printsynth plan part.stl --material PETG --infill 25
"""
from .compiler import compile_print, mesh_metrics   # noqa: F401

__version__ = "0.1.0"
