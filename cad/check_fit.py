"""Interference checks: parts vs board/battery dummies, both lids closed and while sliding.

SPDX-License-Identifier: MIT
Run after build.py (reads ../stl). Needs trimesh + manifold3d.
"""
import os
import numpy as np, trimesh
import ee02_frame_case as M, context as C

STL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'stl')
tray = trimesh.load(os.path.join(STL, 'tray.stl'))
la = trimesh.load(os.path.join(STL, 'lid_board.stl')); la.apply_translation((0, 0, M.Z_LID))
lb = trimesh.load(os.path.join(STL, 'lid_battery.stl')); lb.apply_translation((0, 0, M.Z_LID))
for n, m in [('tray', tray), ('lid_board', la), ('lid_battery', lb)]:
    print(f'{n:12s} watertight={m.is_watertight} vol={m.volume/1000:.1f} cm3')


def inter(a, b):
    try:
        r = trimesh.boolean.intersection([a, b], engine='manifold')
        return 0.0 if r is None or r.is_empty else float(r.volume)
    except Exception as e:
        return f'err {e}'


print('board lid x tray      :', round(inter(la, tray), 3), 'mm3  (detent bump ~5 mm3 is intended)')
print('battery lid x tray    :', round(inter(lb, tray), 3), 'mm3  (detent bump ~5 mm3 is intended)')
print('board lid x batt lid  :', round(inter(la, lb), 3), 'mm3')
dummies = {**C.board_meshes(), **C.battery_meshes(), **C.antenna_meshes()}
bad = 0
for k, m in dummies.items():
    if not m.is_watertight:
        m = m.convex_hull if 'wire' not in k and 'cable' not in k else m
    res = [inter(m, x) for x in (tray, la, lb)]
    if any((isinstance(r, float) and r > 0.002) or isinstance(r, str) for r in res):
        bad += 1
        print(f'  {k:20s} x tray {res[0]}  x lid_board {res[1]}  x lid_battery {res[2]}')
print('dummies with overlap:', bad)

# sliding sweeps
w = 0.0
for dx in np.arange(0, -61, -2.0):
    l2 = la.copy(); l2.apply_translation((dx, 0, 0))
    v = inter(l2, tray); w = max(w, v if isinstance(v, float) else 999)
print('board lid sliding 0..-60 mm in X, max overlap with tray:', round(w, 3))
w = 0.0; w2 = 0.0
for dy in np.arange(0, 141, 3.0):
    l2 = lb.copy(); l2.apply_translation((0, dy, 0))
    v = inter(l2, tray); w = max(w, v if isinstance(v, float) else 999)
    v2 = inter(l2, la); w2 = max(w2, v2 if isinstance(v2, float) else 999)
print('battery lid sliding 0..+140 mm in Y, max overlap with tray:', round(w, 3), ' with board lid:', round(w2, 3))

# board insertion path: lower the PCB from +6 mm to its seat; clip catches must deflect (expected overlap) but nothing else
pcb = C.board_meshes()['board_pcb']
for dz in [0.0, 0.3, 1.0]:
    p2 = pcb.copy(); p2.apply_translation((0, 0, dz))
    print(f'PCB raised {dz:.1f} mm x tray:', round(inter(p2, tray), 3), 'mm3')
print('lead route length', round(M.route_length(), 1), 'mm of', M.BATT_LEAD - 6.0, 'available')
print('highest board part top Z:', round(max(m.bounds[1][2] for m in C.board_meshes().values()), 2), ' lid underside:', M.Z_LID)
print('battery top Z:', round(C.battery_meshes()['battery'].bounds[1][2], 2))
