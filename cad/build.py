"""Build all print files from the CadQuery model.

SPDX-License-Identifier: MIT

Writes
  ../step/<part>.step                 solids for editing in any CAD
  ../stl/<part>.stl                   one mesh per part
  ../print/ee02_case_P1S_plate.3mf    all 9 parts on one Bambu Lab P1S plate (256 x 256 mm)

Usage:  pip install -r requirements.txt && python3 build.py
"""
import os

import numpy as np
import trimesh
import cadquery as cq

import ee02_frame_case as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = {d: os.path.join(ROOT, d) for d in ("step", "stl", "print")}
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- parts
meshes = {}
for name, fn in M.PARTS.items():
    wp = fn()
    assert wp.val().isValid(), f"{name} is not a valid solid"
    cq.exporters.export(wp, os.path.join(DIRS["step"], f"{name}.step"))
    stl = os.path.join(DIRS["stl"], f"{name}.stl")
    cq.exporters.export(wp, stl, tolerance=0.01, angularTolerance=0.1)
    m = trimesh.load(stl)
    meshes[name] = m
    print(f"{name:12s} watertight={m.is_watertight}  {m.volume / 1000:5.1f} cm3")

# ---------------------------------------------------------------- P1S plate
# (part, mesh, lower-left corner on the plate before centring)
items = [
    ("tray", "tray", (0, 0)),
    ("lid_battery", "lid_battery", (133, 0)),
    ("lid_board", "lid_board", (0, 147)),
    ("hanger_portrait", "hanger", (66, 147)),
    ("hanger_landscape", "hanger", (66, 166)),
] + [(f"bumper_{i + 1}", "bumper", (141 + i * 17, 147)) for i in range(4)]

placed = []
for label, part, (dx, dy) in items:
    m = meshes[part].copy()
    lo = m.bounds[0]
    m.apply_translation((dx - lo[0], dy - lo[1], -lo[2]))
    placed.append((label, m))
bounds = np.vstack([m.bounds for _, m in placed])
lo, hi = bounds.min(axis=0), bounds.max(axis=0)
shift = np.array([128 - (lo[0] + hi[0]) / 2, 128 - (lo[1] + hi[1]) / 2, 0])
scene = trimesh.Scene()
for label, m in placed:
    m.apply_translation(shift)
    scene.add_geometry(m, node_name=label, geom_name=label)
size = hi - lo
assert size[0] < 250 and size[1] < 250, "plate layout does not fit the P1S bed"
with open(os.path.join(DIRS["print"], "ee02_case_P1S_plate.3mf"), "wb") as f:
    f.write(trimesh.exchange.threemf.export_3MF(scene))

grams = 1.27 * 0.85 * (sum(meshes[n].volume for n in ("tray", "lid_board", "lid_battery"))
                       + 2 * meshes["hanger"].volume + 4 * meshes["bumper"].volume) / 1000
print(f"plate {size[0]:.0f} x {size[1]:.0f} mm, about {grams:.0f} g PETG")
print(f"battery lead route {M.route_length():.1f} mm")
