"""
3D-print request -> print job.

Takes a mesh (STL, mm) and emits a print JOB: material + settings, a filament + time +
cost estimate (from the mesh volume), a build-volume fit check, and the slicer command
that generates the gcode. Same pattern as molsynth (shape -> recipe): here it's
mesh -> print recipe. Honest: a standard free slicer does the actual slicing.
"""

from __future__ import annotations

import struct

from . import profiles as P


def _read_stl_triangles(path):
    with open(path, "rb") as fh:
        data = fh.read()
    tris = []
    is_binary = False
    if len(data) >= 84:
        n = struct.unpack_from("<I", data, 80)[0]
        if 84 + 50 * n == len(data):
            is_binary = True
    if not is_binary and (b"facet" in data or b"vertex" in data):
        verts = []
        for line in data.decode("ascii", "ignore").splitlines():
            line = line.strip()
            if line.startswith("vertex"):
                _, x, y, z = line.split()[:4]
                verts.append((float(x), float(y), float(z)))
                if len(verts) == 3:
                    tris.append(tuple(verts)); verts = []
    else:
        n = struct.unpack_from("<I", data, 80)[0]
        off = 84
        for _ in range(n):
            v = struct.unpack_from("<12fH", data, off); off += 50
            tris.append(((v[3], v[4], v[5]), (v[6], v[7], v[8]), (v[9], v[10], v[11])))
    return tris


def _signed_volume(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0


def mesh_metrics(tris):
    """Return (volume_cm3, bbox_mm). Volume from the signed-tetrahedron sum (mm^3 -> cm^3)."""
    vol = sum(_signed_volume(*t) for t in tris)
    xs = [p[0] for t in tris for p in t]
    ys = [p[1] for t in tris for p in t]
    zs = [p[2] for t in tris for p in t]
    bbox = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)) if tris else (0, 0, 0)
    return abs(vol) / 1000.0, bbox


def compile_print(stl=None, volume_cm3=None, bbox_mm=None,
                  material=P.DEFAULT_MATERIAL, infill=P.DEFAULT_INFILL,
                  layer_mm=P.DEFAULT_LAYER_MM, name=None):
    """Return a print job dict. Provide an STL, or a volume_cm3 (+ optional bbox)."""
    material = material.upper()
    mat = P.MATERIALS.get(material, P.MATERIALS[P.DEFAULT_MATERIAL])
    if stl is not None:
        tris = _read_stl_triangles(stl)
        volume_cm3, bbox_mm = mesh_metrics(tris)
        name = name or stl.replace("\\", "/").split("/")[-1]
    volume_cm3 = volume_cm3 or 0.0
    bbox_mm = bbox_mm or (0, 0, 0)

    solid_fraction = infill * (1 - P.WALL_FRACTION) + P.WALL_FRACTION
    material_cm3 = volume_cm3 * solid_fraction
    filament_g = material_cm3 * mat["density"]
    time_min = (filament_g / mat["g_per_hr"]) * 60 if mat["g_per_hr"] else 0
    cost = filament_g / 1000.0 * P.PRICE_PER_KG

    bx, by, bz = P.PRINTER["build_mm"]
    fits = bbox_mm[0] <= bx and bbox_mm[1] <= by and bbox_mm[2] <= bz

    slicer_cmd = (f"prusa-slicer --export-gcode --layer-height {layer_mm} "
                  f"--fill-density {int(infill*100)}% --filament-type {material} "
                  f"{name or 'model.stl'}")

    commands = [f"MATERIAL {material}", f"NOZZLE {mat['nozzle_C']}", f"BED {mat['bed_C']}",
                f"SLICE layer={layer_mm} infill={int(infill*100)}%", "PRINT", "DONE"]

    ticket = [
        f"# Print job: {name}",
        f"object: {bbox_mm[0]:.0f}x{bbox_mm[1]:.0f}x{bbox_mm[2]:.0f} mm, {volume_cm3:.1f} cm^3"
        + ("" if fits else "  ⚠ EXCEEDS build volume — scale down or split"),
        f"material: {material}  ({mat['nozzle_C']} C nozzle / {mat['bed_C']} C bed)",
        f"settings: {layer_mm} mm layers, {int(infill*100)}% infill",
        f"estimate: ~{filament_g:.0f} g filament, ~{time_min/60:.1f} h, ~${cost:.2f}",
        f"slice:  {slicer_cmd}",
        "",
        "> A standard FDM printer + free slicer makes this. Form in plastic, not "
        "functional electronics. See ../docs/vision.md.",
    ]
    return {
        "name": name, "material": material, "volume_cm3": round(volume_cm3, 1),
        "bbox_mm": [round(b, 1) for b in bbox_mm], "fits": fits,
        "filament_g": round(filament_g, 1), "time_h": round(time_min / 60, 2),
        "cost_usd": round(cost, 2), "layer_mm": layer_mm, "infill": infill,
        "slicer_cmd": slicer_cmd, "commands": commands, "protocol": "\n".join(ticket),
    }
