"""Context geometry (board, battery, display, frame) for fit checks and renders.

SPDX-License-Identifier: MIT
"""
import math
import os
import tempfile
import numpy as np
import trimesh
import cadquery as cq
import ee02_frame_case as M

TMP = tempfile.mkdtemp(prefix="ee02case_")

# ---------------- frame layout (frame coords: passepartout 300 x 400, viewed from the back) ------------
PP_W, PP_H = 300.0, 400.0
PANEL_W, PANEL_H, PANEL_T = 208.8, 284.7, 0.85
AA_TOP, AA_BOT = 3.0, 11.3                     # active area insets (top / flex edge)
AA_H = 270.4
PANEL_X0 = (PP_W - PANEL_W) / 2                 # 45.6
PANEL_Y0 = (PP_H - AA_H) / 2 - AA_BOT           # 53.5  (active area centred)
TAIL_W, TAIL_FROM_EDGE, FPC_LEN, FPC_WIDE_LEN = 30.5, 40.24, 29.75, 18.0
WIDE_X = (PANEL_X0 + PANEL_W - 176.0, PANEL_X0 + PANEL_W - 39.4)   # wide flex part, back view
TAIL_X = (PANEL_X0 + PANEL_W - TAIL_FROM_EDGE - TAIL_W, PANEL_X0 + PANEL_W - TAIL_FROM_EDGE)
GLASS_T, PP_T = 2.0, 1.4
PROF_W, PROF_D, LIP_W, LIP_T = 20.0, 30.0, 7.0, 5.7     # frame profile from the drawing
FOLD_R = 1.0

# tray position in frame coordinates: J1 centred on the flex tail, J1 slot at the tail end - 4 mm
tail_cx = (TAIL_X[0] + TAIL_X[1]) / 2
j1_cu = (M.J1["u0"] + M.J1["u1"]) / 2
TRAY_X = tail_cx - j1_cu - M.BX0
tail_end_y = PANEL_Y0 + FPC_LEN - math.pi * FOLD_R
TRAY_Y = tail_end_y - 4.0 - M.J1["v0"] - M.BY0
# z (tray) of the passepartout back surface
Z_PP = -M.TAPE


def f2t(x, y):
    """frame (back view) -> tray coords"""
    return (x - TRAY_X, y - TRAY_Y)


def cq_mesh(wp, tol=0.02):
    path = f"{TMP}/_tmp.stl"
    cq.exporters.export(wp, path, tolerance=tol, angularTolerance=0.15)
    return trimesh.load(path)


def tbox(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    b.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return b


def colored(mesh, rgba):
    mesh = mesh.copy()
    mesh.visual.face_colors = np.tile(np.array(rgba, dtype=np.uint8), (len(mesh.faces), 1))
    return mesh


# ---------------- EE02 board dummy (tray coords) -------------------------------------------------
def board_meshes():
    u2 = lambda u, v: M.B(u, v)
    z0 = M.Z_PCB_BOT
    zt = M.Z_PCB_TOP
    pcb = cq.Workplane("XY").box(M.PCB_L, M.PCB_W, M.PCB_T, centered=False).edges("|Z").fillet(2.0)
    pcb = pcb.cut(cq.Workplane("XY").box(M.NOTCH["depth"] + 1, M.NOTCH["v1"] - M.NOTCH["v0"], 5, centered=False)
                  .translate((M.PCB_L - M.NOTCH["depth"], M.NOTCH["v0"], -1)).edges("|Z").fillet(1.2))
    for (u, v) in M.HOLES:
        pcb = pcb.cut(cq.Workplane("XY").circle(M.HOLE_D / 2).extrude(5).translate((u, v, -1)))
    pcb = pcb.translate((M.BX0, M.BY0, z0))
    out = {"board_pcb": colored(cq_mesh(pcb), (22, 24, 28, 255))}

    def bb(name, u0, u1, v0, v1, h0, h1, col):
        x0, y0 = u2(u0, v0)
        x1, y1 = u2(u1, v1)
        out[name] = colored(tbox(x0, x1, y0, y1, zt + h0, zt + h1), col)

    bb("board_j1", M.J1["u0"], M.J1["u1"], M.J1["v0"], M.J1["v1"], 0, M.J1["h"], (236, 236, 232, 255))
    bb("board_j3", M.J3["u0"], M.J3["u1"], M.J3["v0"], M.J3["v1"], 0, 4.6, (238, 226, 196, 255))
    bb("board_plug", M.PLUG["u0"], M.PLUG["u1"], M.PLUG["v0"], M.PLUG["v1"], M.PLUG["z0"], M.PLUG["z1"], (240, 238, 230, 255))
    bb("board_xiao", M.XIAO["u0"], M.XIAO["u1"], M.XIAO["v0"], M.XIAO["v1"], 0, 1.0, (30, 60, 45, 255))
    bb("board_shield", 58.5, 70.5, 22.5, 35.5, 1.0, 3.2, (200, 200, 205, 255))
    bb("board_usbc", USB0 := M.USB_U - 4.47, M.USB_U + 4.47, 35.4, 42.1, 1.0, 4.26, (190, 190, 196, 255))
    # side-actuated slide switch: body near the edge, knob sticks out towards +v (shown in the ON position)
    bb("board_sw1", M.SW1["u0"] + 1.2, M.SW1["u1"] - 1.2, M.SW1["v0"] + 0.7, M.SW1["v1"] - 0.2, 0, 1.6, (40, 40, 44, 255))
    bb("board_sw1_knob", M.SW1["on"] - 0.7, M.SW1["on"] + 0.7, M.SW1["v1"] - 0.2, 41.4, 0.3, 1.3, (230, 230, 230, 255))
    for i, (_, u) in enumerate(M.BUTTONS):
        bb(f"board_key{i}", u - 2.3, u + 2.3, 36.4, 41.0, 0, 3.5, (35, 35, 38, 255))
        bb(f"board_key{i}_act", u - 0.9, u + 0.9, 41.0, M.BTN_PROTRUDE_V, 0.9, 2.6, (35, 35, 38, 255))
    for (u, v) in [(9.0, 31.0), (16.0, 31.0), (27.0, 20.0), (33.0, 20.0)]:
        bb(f"board_ind_{u}", u - 2.5, u + 2.5, v - 2.5, v + 2.5, 0, 2.0, (50, 50, 55, 255))
    bb("board_ic_flash", 38.0, 43.3, 10.0, 15.3, 0, 1.6, (45, 45, 48, 255))
    x, y = u2(*M.UFL)
    ufl = trimesh.creation.cylinder(radius=1.0, height=1.3)
    ufl.apply_translation((x, y, zt + 1.0 + 0.65))
    out["board_ufl"] = colored(ufl, (200, 170, 90, 255))
    return out


def battery_meshes():
    """60.5 x 91 x 6.5 LiPo on its ribs; protection board end towards the EE02, leads leave at the lower right corner"""
    x0, y0, z0 = M.BAT_X0, M.Y_BAT0, M.Z_RIB
    bat = (cq.Workplane("XY").box(M.BATT_W, M.BATT_L, M.BATT_T, centered=False)
           .edges("|Y").fillet(1.2).translate((x0, y0, z0)))
    out = {"battery": colored(cq_mesh(bat), (176, 180, 186, 255))}
    # kapton-wrapped protection board end and the taped long edges
    out["battery_pcm"] = colored(tbox(x0 + 0.02, x0 + M.BATT_W - 0.02, y0 + 0.02, y0 + 5.5, z0 + 0.02, z0 + M.BATT_T + 0.05), (222, 160, 40, 255))
    edges = [tbox(x0 + 0.02, x0 + 2.0, y0 + 5.5, y0 + M.BATT_L - 0.02, z0 + 0.02, z0 + M.BATT_T + 0.05),
             tbox(x0 + M.BATT_W - 2.0, x0 + M.BATT_W - 0.02, y0 + 5.5, y0 + M.BATT_L - 0.02, z0 + 0.02, z0 + M.BATT_T + 0.05)]
    out["battery_tape"] = colored(trimesh.util.concatenate(edges), (222, 160, 40, 255))
    # leads: red / black, side by side, along the route used for the length check
    pts = np.array(M.lead_route())
    d = pts[-1] - pts[0]
    nrm = np.array([-d[1], d[0], 0.0])
    nrm /= np.linalg.norm(nrm)
    for name, off, col in [("battery_wire_red", -0.6, (200, 40, 40, 255)), ("battery_wire_blk", 0.6, (25, 25, 25, 255))]:
        p = pts + nrm * off
        p[-1] = pts[-1] + np.array([0.0, off * 1.1, 0.0])
        segs = [trimesh.creation.cylinder(radius=0.55, segment=[a, b], sections=10) for a, b in zip(p[:-1], p[1:])]
        segs += [trimesh.creation.icosphere(subdivisions=1, radius=0.55).apply_translation(q) for q in p[1:-1]]
        out[name] = colored(trimesh.util.concatenate(segs), col)
    return out


# ---------------- display / frame context (tray coords) -------------------------------------------
def display_meshes(crop=None):
    """crop=(xmin,xmax,ymin,ymax) in tray coords, None = whole frame"""
    out = {}
    fx0, fy0 = f2t(0, 0)
    fx1, fy1 = f2t(PP_W, PP_H)
    px0, py0 = f2t(PANEL_X0, PANEL_Y0)
    px1, py1 = f2t(PANEL_X0 + PANEL_W, PANEL_Y0 + PANEL_H)

    def clip(x0, x1, y0, y1):
        if crop is None:
            return x0, x1, y0, y1
        return max(x0, crop[0]), min(x1, crop[1]), max(y0, crop[2]), min(y1, crop[3])

    zpp = Z_PP
    out["passepartout"] = colored(tbox(*clip(fx0, fx1, fy0, fy1), zpp - PP_T, zpp), (246, 244, 238, 255))
    out["glass"] = colored(tbox(*clip(fx0, fx1, fy0, fy1), zpp - PP_T - GLASS_T, zpp - PP_T), (200, 225, 235, 70))
    out["panel"] = colored(tbox(*clip(px0, px1, py0, py1), zpp, zpp + PANEL_T), (92, 96, 104, 255))
    # frame profile (L section) around the passepartout
    zlip0 = zpp - PP_T - GLASS_T - LIP_T
    zback = zlip0 + PROF_D
    body_w = PROF_W - LIP_W
    bars = [
        (fx0 - body_w, fx1 + body_w, fy0 - body_w, fy0),   # bottom
        (fx0 - body_w, fx1 + body_w, fy1, fy1 + body_w),   # top
        (fx0 - body_w, fx0, fy0, fy1),                     # left
        (fx1, fx1 + body_w, fy0, fy1),                     # right
    ]
    wood = []
    for (x0, x1, y0, y1) in bars:
        c = clip(x0, x1, y0, y1)
        if c[0] < c[1] and c[2] < c[3]:
            wood.append(tbox(*c, zlip0, zback))
    lips = [(fx0 - body_w, fx1 + body_w, fy0 - body_w, fy0 + LIP_W), (fx0 - body_w, fx1 + body_w, fy1 - LIP_W, fy1 + body_w),
            (fx0 - body_w, fx0 + LIP_W, fy0, fy1), (fx1 - LIP_W, fx1 + body_w, fy0, fy1)]
    for (x0, x1, y0, y1) in lips:
        c = clip(x0, x1, y0, y1)
        if c[0] < c[1] and c[2] < c[3]:
            wood.append(tbox(*c, zlip0, zlip0 + LIP_T))
    out["frame"] = colored(trimesh.util.concatenate(wood), (176, 132, 88, 255))
    out.update(fpc_meshes(crop))
    return out


def fpc_meshes(crop=None):
    """flex folded 180 deg around the panel's lower edge, tail rising into J1"""
    out = {}
    zb = Z_PP + PANEL_T               # panel back
    y_edge = f2t(0, PANEL_Y0)[1]
    th = 0.12
    # centre-line in (Y,Z): under the ledge -> around the edge -> along the back -> S-curve -> J1
    pts = []
    for a in np.linspace(-math.pi / 2, math.pi / 2, 14):     # fold loop
        r = (PANEL_T - 0.3) / 2 + 0.25
        zc = Z_PP + 0.3 + r - 0.15
        pts.append((y_edge - 0.3 - r * math.cos(a) * 1.6, zc + r * math.sin(a)))
    y_wide_end = y_edge + FPC_WIDE_LEN - math.pi * FOLD_R
    y_j1 = M.BY0 + M.J1["v0"]
    z_j1 = M.Z_PCB_TOP + 0.9
    y_s0 = y_wide_end - 3.0
    y_s1 = y_j1 - 2.0
    for y in np.linspace(y_edge + 1.0, y_s0, 6):
        pts.append((y, zb + th))
    for tt in np.linspace(0, 1, 18)[1:]:
        s = (1 - math.cos(math.pi * tt)) / 2
        pts.append((y_s0 + (y_s1 - y_s0) * tt, zb + th + (z_j1 - zb - th) * s))
    pts.append((y_j1 + 4.0, z_j1))
    pts = np.array(pts)
    # thin strip polygon (offset both sides)
    def strip(p):
        n = []
        for i in range(len(p)):
            a = p[max(i - 1, 0)]
            b = p[min(i + 1, len(p) - 1)]
            d = b - a
            d = d / (np.linalg.norm(d) + 1e-9)
            n.append((-d[1], d[0]))
        n = np.array(n)
        return np.vstack([p + n * th / 2, (p - n * th / 2)[::-1]])

    tx0, _ = f2t(TAIL_X[0], 0)
    tx1, _ = f2t(TAIL_X[1], 0)
    wx0, _ = f2t(WIDE_X[0], 0)
    wx1, _ = f2t(WIDE_X[1], 0)
    if crop is not None:
        wx0 = max(wx0, crop[0])
    # narrow tail: full path
    tail = cq.Workplane("YZ", origin=(tx0, 0, 0)).polyline([tuple(q) for q in strip(pts)]).close().extrude(tx1 - tx0)
    out["flex_tail"] = colored(cq_mesh(tail, 0.05), (214, 128, 36, 255))
    # wide part: only up to the end of the wide section
    k = np.searchsorted(pts[:, 0] * 0 + np.arange(len(pts)), 0)
    wide_pts = [q for q in pts if not (q[0] > y_wide_end and q[1] > zb + th + 0.01)]
    wide_pts = np.array([q for q in wide_pts if q[0] <= y_wide_end] if True else wide_pts)
    wide = cq.Workplane("YZ", origin=(wx0, 0, 0)).polyline([tuple(q) for q in strip(wide_pts)]).close().extrude(wx1 - wx0)
    out["flex_wide"] = colored(cq_mesh(wide, 0.05), (206, 120, 30, 255))
    # stiffener at the tail end
    out["flex_stiffener"] = colored(tbox(tx0, tx1, y_j1 - 1.8, y_j1 + 4.0, z_j1 + 0.06, z_j1 + 0.3), (60, 40, 25, 255))
    return out


def antenna_meshes():
    ax, _ = M.B(M.UFL[0] + 2.5, 0)
    x0, y0 = f2t(258.0, 14.0)            # flat on the passepartout, below the battery end
    ant = colored(tbox(x0, x0 + 22, y0, y0 + 38, Z_PP, Z_PP + 0.3), (20, 20, 22, 255))
    pts = np.array([[ax, 1.5, 5.3], [ax, -3.0, 4.6], [ax + 4, -10.0, 1.2], [x0 + 8, y0 + 44, Z_PP + 0.6],
                    [x0 + 8, y0 + 36, Z_PP + 0.45]])
    segs = [trimesh.creation.cylinder(radius=0.6, segment=[a, b], sections=8) for a, b in zip(pts[:-1], pts[1:])]
    ufl_pts = np.array([[*M.B(*M.UFL), M.Z_PCB_TOP + 2.2], [M.B(*M.UFL)[0] + 1.5, 10, M.Z_PCB_TOP + 3.3],
                        [ax, 4.0, 6.4], [ax, 1.5, 5.3]])
    segs += [trimesh.creation.cylinder(radius=0.6, segment=[a, b], sections=8) for a, b in zip(ufl_pts[:-1], ufl_pts[1:])]
    return {"antenna": ant, "antenna_cable": colored(trimesh.util.concatenate(segs), (30, 30, 30, 255))}


if __name__ == "__main__":
    print("tray origin in frame coords (back view):", round(TRAY_X, 2), round(TRAY_Y, 2))
    print("tray right edge x =", round(TRAY_X + M.L, 2), " (rebate wall at 300)")
    print("panel right edge in tray X =", round(PANEL_X0 + PANEL_W - TRAY_X, 2))
    print("panel bottom edge in tray Y =", round(PANEL_Y0 - TRAY_Y, 2))
