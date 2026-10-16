"""
EE02 e-paper frame case - parametric CadQuery model (Rev B)
==========================================================
SPDX-License-Identifier: MIT
Part of https://github.com/gaduffl/ee02-eink-frame (the printable parts it generates are CC BY-SA 4.0).

Parts (all print without supports on a Bambu Lab P1S, 256 x 256 x 256 mm):
  tray         - taped to the passepartout's side margin; holds the Seeed XIAO ePaper Display
                 Board EE02 and a flat LiPo (60.5 x 91 x 6.5 mm, JST-PH, leads at a corner)
  lid_board    - small dovetail lid over the EE02's left part, slides out to the left
  lid_battery  - dovetail lid over the battery and the JST socket, slides up and off
  hanger       - keyhole wall hanger with 7 levelling notches (print 2: portrait + landscape)
  bumper       - 5 mm wall spacer (print 4, one per frame corner)

Coordinate system (tray): origin = outer corner of the tray, viewed from the BACK of the
frame (frame lying face down, display flex edge at the bottom).
  X -> to the right (towards the frame's side rebate), Y -> up (towards the display centre),
  Z -> away from the passepartout (towards the frame back).

Board data comes from Seeed's KiCad file "XIAO ePaper Display Board EE02_V1.0" (board 80 x 41.23 x 1.6 mm,
4 x d2.5 mm holes). Display data from Seeed T133A01 datasheet (flex tail 30.5 mm wide, 29.75 mm long,
40.24 mm from the panel edge).

Run:  python3 ee02_frame_case.py      -> writes STEP/STL files into ../step and ../stl
      python3 build.py                 -> the same plus the Bambu Lab P1S plate in ../print
"""
import os
import math
import cadquery as cq

# --------------------------------------------------------------------------------------
# Parameters you may want to change
# --------------------------------------------------------------------------------------
TAPE = 1.0            # thickness of the double-sided foam tape under the right part (mm)
BATT_W = 60.5         # LiPo width  (across, X)
BATT_L = 91.0         # LiPo length (along Y; protection board end towards the EE02)
BATT_T = 6.5          # LiPo thickness
BATT_LEAD = 62.0      # cell corner -> end of the JST plug (only used for the route check)
BAT_CLR_SIDE = 0.6    # battery to pocket walls (per side)
BAT_CLR_END = 0.8     # battery to the top wall
FIT = 0.3             # sliding clearance of the dovetail lids (per side)

# --------------------------------------------------------------------------------------
# EE02 board (board-local u along 80 mm edge, v along 41.23 mm edge, component side up,
# FPC connector J1 on the v=0 edge, USB-C / keys / power switch on the v=41.23 edge)
# --------------------------------------------------------------------------------------
PCB_L, PCB_W, PCB_T = 80.0, 41.23, 1.6
HOLES = [(2.54, 2.55), (77.44, 2.55), (2.54, 38.76), (77.44, 38.76)]
HOLE_D = 2.5
NOTCH = dict(v0=9.73, v1=16.26, depth=3.29)          # battery-plug notch in the u=80 edge
J1 = dict(u0=6.5, u1=40.0, v0=0.37, v1=5.22, h=2.0)   # 60-pin FPC connector (slot at v0)
J3 = dict(u0=69.5, u1=77.3, v0=8.9, v1=17.0, h=5.5)   # JST-PH battery socket, plug from +u
PLUG = dict(u0=76.0, u1=81.8, v0=10.7, v1=15.3, z0=0.4, z1=4.4)   # mated JST-PH plug
XIAO = dict(u0=56.7, u1=74.5, v0=20.2, v1=41.13)      # XIAO ESP32-S3 Plus module
USB_U = 65.6                                           # USB-C centre (points +v)
UFL = (61.0, 21.6)                                     # antenna U.FL on the XIAO
SW1 = dict(u0=5.8, u1=14.8, v0=36.3, v1=39.8, on=8.7, off=13.8)  # side-actuated power switch, knob at +v
BUTTONS = [("RST", 20.40), ("3", 29.74), ("2", 39.07), ("1", 48.40)]  # side keys, protrude to v=42.68
BTN_PROTRUDE_V = 42.68
KEY_OPEN_U = (6.0, 51.0)                               # 45 mm opening for keys + switch
THT_ZONE = dict(u0=6.5, u1=51.5, v0=35.0, v1=41.2)     # through-hole pins under the board

# --------------------------------------------------------------------------------------
# Frame placement (only the side rebate matters for the tray size)
# rebate (x=300 in frame coords) minus centre of the display flex tail (198.91)
# --------------------------------------------------------------------------------------
J1C_TO_REBATE = 101.09
REBATE_CLR = 2.0      # gap between the tray and the frame's rebate wall

# --------------------------------------------------------------------------------------
# Tray layout
# --------------------------------------------------------------------------------------
WALL_L = 2.0          # left wall of the board section
WALL_D = 2.6          # walls that carry a dovetail groove (and the battery top wall)
FLOOR = 1.2
INNER_H = 11.0        # floor top -> lid underside
LID_T = 2.0
DOVE = 1.4            # dovetail undercut (45 deg)

CLR_FPC = 0.8         # board J1 edge to bottom wall
CLR_BTN = 0.8         # side keys to top wall
STANDOFF_H = 1.0      # board sits 1 mm above the floor (THT pins get 1.9 mm with the pocket)
PIN_D = 1.9           # locating pins in the d2.5 board holes
PIN_H = 1.4

# snap clips: beam printed on the bed, cut free from the floor, flexes sideways
CLIP_T = 1.4          # beam thickness
CLIP_SLOT = 1.1       # free space behind the beam (= max deflection)
CLIP_GAP = 0.6        # beam face -> board edge
CLIP_O = 1.4          # catch depth: tip reaches CLIP_O - CLIP_GAP = 0.8 mm over the board
CLIP_C = 0.25         # vertical play between board top and catch
CLIP_CATCH_L = 6.0    # catch length along the beam
# (side, v at the root, v at the tip)
CLIPS = [("L", 6.5, 19.0), ("L", 34.5, 22.0), ("R", 36.0, 18.5)]

BX0 = WALL_L + CLIP_SLOT + CLIP_T + CLIP_GAP   # board origin in tray coords
BY0 = WALL_D + CLR_FPC
Z_PCB_BOT = FLOOR + STANDOFF_H
Z_PCB_TOP = Z_PCB_BOT + PCB_T
Z_LID = FLOOR + INNER_H               # lid underside
H = Z_LID + LID_T                     # overall tray height

Y_TOP_IN = BY0 + BTN_PROTRUDE_V + CLR_BTN   # inner face of the board section's top wall
Y_BS = Y_TOP_IN + WALL_D                    # board section outer top

X_BOARD_END = BX0 + PCB_L
X_R = BX0 + (J1["u0"] + J1["u1"]) / 2 + J1C_TO_REBATE - REBATE_CLR   # tray right edge
X_RIN = X_R - WALL_D                        # inner face of the right wall

# battery pocket: as far left as the key opening allows (shortest lead route)
KEY_X1 = BX0 + KEY_OPEN_U[1]
X_CO = KEY_X1 + 1.5                         # pocket's left wall, outer face
X_CIN = X_CO + WALL_D                       # ... inner face
BAT_X0 = X_CIN + BAT_CLR_SIDE               # battery left edge
BAT_X1 = BAT_X0 + BATT_W
Y_BAT0 = Y_TOP_IN + 0.3                     # battery end with the protection board + leads
Y_BAT1 = Y_BAT0 + BATT_L
Y_TIN = Y_BAT1 + BAT_CLR_END
Y_T = Y_TIN + WALL_D                        # overall tray size in Y
Z_RIB = FLOOR + 3.0                         # battery rests on ribs (1.5 mm under the lid)

# B'-lid support / battery stop blocks in the bay (x ranges)
BAY_X0 = X_BOARD_END + CLIP_GAP + CLIP_T + CLIP_SLOT
STOPS = [(BAY_X0 + 4.0, BAY_X0 + 12.0), (BAY_X0 + 16.0, BAY_X0 + 24.0)]

USB_ZONE = (BX0 + USB_U - 6.5, BX0 + USB_U + 6.5)   # keep free for a USB-C plug (battery out)
NOTCH_Y = (Y_BAT0 + 22.0, Y_BAT0 + 59.0)            # finger / cable notch in the pocket's left wall


def B(u, v):
    """board-local -> tray coordinates"""
    return (BX0 + u, BY0 + v)


def plug_back():
    """tray coords of the wire end of the mated JST plug"""
    x, y = B(PLUG["u1"], (PLUG["v0"] + PLUG["v1"]) / 2)
    return (x, y, Z_PCB_TOP + (PLUG["z0"] + PLUG["z1"]) / 2)


def lead_route():
    """battery leads: from the cell's lower right corner diagonally through the bay into the plug"""
    px, py, pz = plug_back()
    zc = Z_RIB + BATT_T / 2
    cx, cy = BAT_X1 - 0.6, Y_BAT0 + 0.4
    return [(cx, cy, zc), (cx - 1.2, cy - 1.6, zc - 0.4), (px + 5.2, py + 3.4, pz + 0.3),
            (px + 2.6, py + 0.5, pz), (px, py, pz)]


def route_length():
    p = lead_route()
    return sum(math.dist(a, b) for a, b in zip(p[:-1], p[1:]))


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def prism_yz(pts_yz, x0, x1):
    """polygon in the (Y,Z) plane extruded from x0 to x1"""
    return (cq.Workplane("YZ", origin=(x0, 0, 0)).polyline(pts_yz).close().extrude(x1 - x0))


def prism_xz(pts_xz, y0, y1):
    """polygon in the (X,Z) plane extruded from y0 to y1 (XZ plane extrudes towards -Y)"""
    return (cq.Workplane("XZ", origin=(0, y1, 0)).polyline(pts_xz).close().extrude(y1 - y0))


def slot_xz(xc, zc, w, h, y0, y1):
    """vertical stadium slot through a wall parallel to XZ"""
    return (cq.Workplane("XZ", origin=(0, y1, 0)).center(xc, zc)
            .slot2D(h, w, angle=90).extrude(y1 - y0))


def cyl(x, y, z0, h, d):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def opening_zc():
    """USB-C / key opening: same height band"""
    return Z_PCB_TOP + 1.0 + 1.63


OPEN_H = 7.6


# --------------------------------------------------------------------------------------
# snap clip (beam + catch); returns (solid to add, floor slot to cut)
# --------------------------------------------------------------------------------------
def clip_geometry(side, v_root, v_tip):
    _, y_root = B(0, v_root)
    _, y_tip = B(0, v_tip)
    ylo, yhi = min(y_root, y_tip), max(y_root, y_tip)
    s = 1 if y_tip > y_root else -1                    # beam direction root -> tip
    z_low = Z_PCB_TOP + CLIP_C - CLIP_GAP             # catch underside at the beam face
    z_top = z_low + 2 * CLIP_O
    if side == "L":
        xf = BX0 - CLIP_GAP                            # beam face towards the board
        xb = xf - CLIP_T
        slot_x = (WALL_L - 0.01, BX0)
        catch = [(xf - 0.01, z_low), (xf + CLIP_O, z_low + CLIP_O), (xf - 0.01, z_top)]
        post_x = (WALL_L - 0.01, xf)
    else:
        xf = X_BOARD_END + CLIP_GAP
        xb = xf + CLIP_T
        slot_x = (X_BOARD_END, xb + CLIP_SLOT)
        catch = [(xf + 0.01, z_low), (xf - CLIP_O, z_low + CLIP_O), (xf + 0.01, z_top)]
        post_x = (xf, xb + 1.6)
    x0, x1 = min(xf, xb), max(xf, xb)
    # floor slot around the beam (open on both long sides and at the tip)
    sy0, sy1 = (y_root, y_tip + 1.0) if s > 0 else (y_tip - 1.0, y_root)
    slot = box(slot_x[0], slot_x[1], sy0, sy1, -1.0, FLOOR + 0.02)
    beam = box(x0, x1, ylo, yhi, 0.0, z_top)
    cy0, cy1 = (y_tip - CLIP_CATCH_L, y_tip) if s > 0 else (y_tip, y_tip + CLIP_CATCH_L)
    beam = beam.union(prism_xz(catch, cy0, cy1))
    # root post (fused to the wall on the left, free standing on the right)
    py0, py1 = (y_root - 2.5, y_root + 0.01) if s > 0 else (y_root - 0.01, y_root + 2.5)
    post = box(post_x[0], post_x[1], py0, py1, 0.0, z_top)
    return beam.union(post), slot


# --------------------------------------------------------------------------------------
# TRAY
# --------------------------------------------------------------------------------------
def make_tray():
    outline = [(0, 0), (X_R, 0), (X_R, Y_T), (X_CO, Y_T), (X_CO, Y_BS), (0, Y_BS)]
    t = cq.Workplane("XY").polyline(outline).close().extrude(H).edges("|Z").fillet(2.5)

    # ---- interiors ----
    t = t.cut(box(WALL_L, X_RIN, WALL_D, Y_TOP_IN, FLOOR, H + 1))               # board section + bay
    t = t.cut(box(X_CIN, X_RIN, Y_TOP_IN - 0.01, Y_TIN, FLOOR, H + 1))         # battery pocket
    # board lid exit: left wall lowered to the lid underside
    t = t.cut(box(-1, WALL_L + 0.01, WALL_D, Y_TOP_IN, Z_LID, H + 1))
    # battery lid exit: battery top wall lowered to the lid underside
    t = t.cut(box(X_CIN, X_RIN, Y_TIN - 0.01, Y_T + 1, Z_LID, H + 1))

    # ---- dovetail grooves (45 deg undercut) ----
    # board lid: bottom wall and board top wall, open at the left end, closed at the pocket wall
    t = t.cut(prism_yz([(WALL_D - DOVE, Z_LID), (WALL_D + 0.01, Z_LID), (WALL_D + 0.01, Z_LID + DOVE)], -1, X_CO))
    t = t.cut(prism_yz([(Y_TOP_IN + DOVE, Z_LID), (Y_TOP_IN - 0.01, Z_LID), (Y_TOP_IN - 0.01, Z_LID + DOVE)], -1, X_CO))
    # battery lid: pocket's left wall and the right wall, open at the top end
    t = t.cut(prism_xz([(X_CIN - DOVE, Z_LID), (X_CIN + 0.01, Z_LID), (X_CIN + 0.01, Z_LID + DOVE)], Y_TOP_IN - 1.0, Y_T + 1))
    t = t.cut(prism_xz([(X_RIN + DOVE, Z_LID), (X_RIN - 0.01, Z_LID), (X_RIN - 0.01, Z_LID + DOVE)], WALL_D + 0.01, Y_T + 1))
    # lead-in chamfers at both lid entries
    t = t.cut(prism_xz([(-0.01, Z_LID + DOVE), (1.2, H + 0.01), (-0.01, H + 0.01)], -1, Y_BS + 1))
    t = t.cut(prism_yz([(Y_T + 0.01, Z_LID + DOVE), (Y_T - 1.2, H + 0.01), (Y_T + 0.01, H + 0.01)], X_CO - 1, X_R + 1))

    # ---- FPC window in the bottom wall (in front of J1) ----
    j1x0, _ = B(J1["u0"] - 0.5, 0)
    j1x1, _ = B(J1["u1"] + 2.0, 0)
    t = t.cut(box(j1x0, j1x1, -1, WALL_D + 0.01, -1, 8.0))
    # ---- antenna lead slot in the bottom wall, open to the top (lead drops in) ----
    ax, _ = B(UFL[0] + 2.5, 0)
    t = t.cut(slot_xz(ax, (4.6 + H + 6) / 2, 4.4, (H + 6) - 4.6, -1, WALL_D + 0.01))
    # ---- 45 mm opening for the side keys and the power switch, outside edges flared ----
    zc = opening_zc()
    kx0, _ = B(KEY_OPEN_U[0], 0)
    kx1, _ = B(KEY_OPEN_U[1], 0)
    kw = kx1 - kx0
    flare = 1.5
    t = t.cut(cq.Workplane("XZ", origin=(0, Y_BS - flare + 0.01, 0)).center((kx0 + kx1) / 2, zc)
              .rect(kw, OPEN_H).extrude(Y_BS - flare + 0.01 - (Y_TOP_IN - 0.5)))
    t = t.cut(cq.Workplane("XZ", origin=(0, Y_BS + 0.6, 0)).center((kx0 + kx1) / 2, zc)
              .rect(kw + 2 * (flare + 0.6), OPEN_H + 2 * (flare + 0.6)).extrude(flare + 0.6, taper=45))

    # ---- board support: standoffs with locating pins, centre pads ----
    for (u, v) in HOLES:
        x, y = B(u, v)
        t = t.union(cyl(x, y, FLOOR - 0.01, STANDOFF_H + 0.01, 4.6))
        pin = (cq.Workplane("XY").circle(PIN_D / 2).extrude(PIN_H).faces(">Z").chamfer(0.5)
               .translate((x, y, Z_PCB_BOT - 0.01)))
        t = t.union(pin)
    for (u, v) in [(40.0, 12.0), (40.0, 28.0)]:
        x, y = B(u, v)
        t = t.union(cyl(x, y, FLOOR - 0.01, STANDOFF_H + 0.01, 5.0))
    # pocket for the through-hole pins of the switch and keys
    x0, y0 = B(THT_ZONE["u0"], THT_ZONE["v0"])
    x1, y1 = B(THT_ZONE["u1"], THT_ZONE["v1"])
    t = t.cut(box(x0, x1, y0, y1, FLOOR - 0.9, FLOOR + 0.01))

    # ---- snap clips: cut the floor slots first, then add beams ----
    beams = []
    for side, vr, vt in CLIPS:
        b, s = clip_geometry(side, vr, vt)
        t = t.cut(s)
        beams.append(b)
    for b in beams:
        t = t.union(b)

    # ---- bay: lid supports that also stop the battery's lower edge, one more lid post ----
    for (sx0, sx1) in STOPS:
        t = t.union(box(sx0, sx1, Y_TOP_IN - 2.4, Y_TOP_IN + 0.01, FLOOR - 0.01, Z_LID))
    t = t.union(cyl(STOPS[1][1] + 1.0, WALL_D + 9.0, FLOOR - 0.01, Z_LID - FLOOR + 0.01, 5.0))

    # ---- battery pocket: ribs to lift the cell, spacers on the right, finger/cable notch ----
    rib_x = [X_CIN + 1.4, BAT_X0 + 17.7, BAT_X0 + 32.7, BAT_X0 + 47.7, BAT_X1 - 2.0]
    for rx in rib_x:
        t = t.union(box(rx - 0.8, rx + 0.8, Y_BAT0 + 1.0, Y_BAT1 - 1.0, FLOOR - 0.01, Z_RIB))
    # extra rib in the USB-C zone, starts behind where a USB-C plug body would sit
    rx = (USB_ZONE[0] + USB_ZONE[1]) / 2
    t = t.union(box(rx - 0.8, rx + 0.8, NOTCH_Y[1] + 4.0, Y_BAT1 - 1.0, FLOOR - 0.01, Z_RIB))
    # right side spacers (battery sits against the left wall, as close to the board as possible)
    for yc in [Y_BAT0 + 20.0, Y_BAT0 + 50.0, Y_BAT0 + 80.0]:
        t = t.union(box(BAT_X1 + BAT_CLR_SIDE, X_RIN + 0.01, yc - 3.0, yc + 3.0, FLOOR - 0.01, Z_LID - 1.6))
    # notch in the pocket's left wall: grip the cell, or let a USB-C cable out (battery removed)
    nz = Z_RIB + 0.5
    ny0, ny1 = NOTCH_Y
    d = H + 1 - nz
    t = t.cut(prism_yz([(ny0, H + 1), (ny0 + d, nz), (ny1 - d, nz), (ny1, H + 1)], X_CO - 1, X_CIN + 0.01)
              if ny1 - ny0 > 2 * d else
              prism_yz([(ny0 - d, H + 1), (ny0, nz), (ny1, nz), (ny1 + d, H + 1)], X_CO - 1, X_CIN + 0.01))

    # ---- lid detent bumps (left wall for the board lid, battery top wall for the battery lid) ----
    t = t.union(prism_xz([(0.35, Z_LID - 0.01), (1.65, Z_LID - 0.01), (1.15, Z_LID + 0.35), (0.85, Z_LID + 0.35)],
                         Y_TOP_IN / 2 - 8.0, Y_TOP_IN / 2 + 8.0))
    yd = Y_TIN + WALL_D / 2
    for xc in (X_CIN + 12.0, X_RIN - 12.0):          # two short bumps: little drag over the long stroke
        t = t.union(prism_yz([(yd - 0.65, Z_LID - 0.01), (yd + 0.65, Z_LID - 0.01), (yd + 0.15, Z_LID + 0.35),
                              (yd - 0.15, Z_LID + 0.35)], xc - 3.0, xc + 3.0))

    # ---- cosmetics: soften the bottom edges (anti elephant foot, frees the clip beams) ----
    try:
        t = t.faces("<Z").edges().chamfer(0.4)
    except Exception:
        pass
    return t


# --------------------------------------------------------------------------------------
# LIDS (printed underside down)
# --------------------------------------------------------------------------------------
def label(txt, x, y, size=2.4, angle=0):
    w = cq.Workplane("XY").workplane(offset=LID_T - 0.01)
    return (w.center(x, y).transformed(rotate=(0, 0, angle))
            .text(txt, size, 0.5, halign="center", valign="center", fontPath=FONT))


def chevrons(xc, yc, direction, n=3, pitch=5.5):
    """raised grip chevrons pointing in 'direction' ('-X' or '+Y')"""
    out = None
    for i in range(n):
        if direction == "-X":
            x = xc + i * pitch
            pts = [(x, yc), (x + 6, yc + 9), (x + 7.6, yc + 9), (x + 1.6, yc), (x + 7.6, yc - 9), (x + 6, yc - 9)]
        else:
            y = yc - i * pitch
            pts = [(xc, y), (xc + 9, y - 6), (xc + 9, y - 7.6), (xc, y - 1.6), (xc - 9, y - 7.6), (xc - 9, y - 6)]
        c = cq.Workplane("XY").polyline(pts).close().extrude(0.7).translate((0, 0, LID_T - 0.01))
        out = c if out is None else out.union(c)
    return out


def make_lid_board():
    """slides out to the left; right end overlaps the battery lid's dovetail edge from above"""
    y0 = WALL_D - DOVE + FIT
    y1 = Y_TOP_IN + DOVE - FIT
    xf = X_CO - FIT                                 # flanges end before the pocket wall
    prof = [(y0, 0), (y1, 0), (y1 - DOVE, DOVE), (y1 - DOVE, LID_T), (y0 + DOVE, LID_T), (y0 + DOVE, DOVE)]
    lid = prism_yz(prof, 0, xf)
    # right part without flanges, ending in a 45 deg bevel that rests on the battery lid
    xb = X_CIN - DOVE                               # = battery lid edge - FIT, at the lid underside
    right = prism_xz([(xf - 0.01, 0), (xb, 0), (xb + DOVE, DOVE), (xb + DOVE, LID_T), (xf - 0.01, LID_T)],
                     y0 + DOVE, y1 - DOVE)
    lid = lid.union(right)
    lid = lid.faces("<X").edges("|Y").chamfer(0.4)                 # soften the grip end
    # detent groove on the underside, above the left wall bump
    lid = lid.cut(prism_xz([(0.2, -0.01), (1.8, -0.01), (1.3, 0.45), (0.7, 0.45)], Y_TOP_IN / 2 - 8.5, Y_TOP_IN / 2 + 8.5))
    # grip chevrons pointing to the opening direction (-X)
    lid = lid.union(chevrons(16.0, Y_TOP_IN / 2 - 4.0, "-X"))
    # labels next to the keys and the switch (they sit right below the lid's top edge)
    yl = Y_TOP_IN - FIT - 3.4
    lid = lid.union(label("ON", B(SW1["on"] - 1.6, 0)[0], yl, 2.3))
    lid = lid.union(label("OFF", B(SW1["off"] + 2.3, 0)[0], yl, 2.3))
    for name, u in BUTTONS:
        lid = lid.union(label("R" if name == "RST" else name, B(u, 0)[0], yl, 2.3))
    return lid


def make_lid_battery():
    """slides up (+Y) and off; covers the battery, the JST socket and the bay"""
    xa = X_CIN - DOVE + FIT
    xb = X_RIN + DOVE - FIT
    prof = [(xa, 0), (xb, 0), (xb - DOVE, DOVE), (xb - DOVE, LID_T), (xa + DOVE, LID_T), (xa + DOVE, DOVE)]
    ya = WALL_D + FIT
    lid = prism_xz(prof, ya, Y_T)
    lid = lid.faces(">Y").edges("|X").chamfer(0.4)                 # soften the grip end
    # detent groove on the underside, above the top wall bump
    yd = Y_TIN + WALL_D / 2
    lid = lid.cut(prism_yz([(yd - 0.8, -0.01), (yd + 0.8, -0.01), (yd + 0.3, 0.45), (yd - 0.3, 0.45)],
                           X_CIN + 9.5, X_RIN - 9.5))
    # grip chevrons pointing up (+Y), near the top end
    xc = (X_CIN + X_RIN) / 2
    lid = lid.union(chevrons(xc, Y_T - 8.0, "+Y"))
    lid = lid.union(label("BATTERY", xc, Y_T - 34.0, 3.0))
    return lid


# --------------------------------------------------------------------------------------
# HANGER  (hanger coords: X along the frame edge, Y towards the frame's outer edge,
#          Z = 0 on the wall side, 5 mm = side screwed onto the frame back)
# --------------------------------------------------------------------------------------
HANGER = dict(L=68.0, W=14.0, T=5.0, flange=1.6,
              ch_y0=1.6, ch_y1=12.2, ch_x0=-22.8, ch_x1=17.0,
              seat_y=7.4, seat_r=2.25, notch_x=[-12, -8, -4, 0, 4, 8, 12],
              slot_y0=3.8, slot_y1=8.4, slot_x0=-17.5, slot_x1=14.25,
              entry=(-17.5, 6.9, 9.0), screws=[-29.0, 29.0], screw_d=3.4, csk_d=6.8)


def make_hanger():
    h = HANGER
    p = box(-h["L"] / 2, h["L"] / 2, 0, h["W"], 0, h["T"]).edges("|Z").fillet(3.0)
    p = p.faces(">Z").edges().chamfer(0.6)
    # head channel (open towards the frame)
    chw = h["ch_y1"] - h["ch_y0"]
    chl = h["ch_x1"] - h["ch_x0"]
    p = p.cut(cq.Workplane("XY").center((h["ch_x0"] + h["ch_x1"]) / 2, (h["ch_y0"] + h["ch_y1"]) / 2)
              .slot2D(chl, chw).extrude(h["T"]).translate((0, 0, h["flange"])))
    # shank slot + levelling notches through the flange
    cutter = (cq.Workplane("XY").center((h["slot_x0"] + h["slot_x1"]) / 2, (h["slot_y0"] + h["slot_y1"]) / 2)
              .rect(h["slot_x1"] - h["slot_x0"], h["slot_y1"] - h["slot_y0"]).extrude(h["flange"] + 0.2).translate((0, 0, -0.1)))
    for nx in h["notch_x"]:
        cutter = cutter.union(cyl(nx, h["seat_y"], -0.1, h["flange"] + 0.2, 2 * h["seat_r"]))
    ex, ey, ed = h["entry"]
    cutter = cutter.union(cyl(ex, ey, -0.1, h["flange"] + 0.2, ed))
    p = p.cut(cutter)
    # countersunk screw holes (head on the wall side, Z=0)
    for sx in h["screws"]:
        p = p.cut(cyl(sx, h["W"] / 2, -1, h["T"] + 2, h["screw_d"]))
        csk = cq.Solid.makeCone(h["csk_d"] / 2 + 0.3, 0, (h["csk_d"] / 2 + 0.3), pnt=cq.Vector(sx, h["W"] / 2, -0.3),
                                dir=cq.Vector(0, 0, 1))
        p = p.cut(cq.Workplane("XY").add(csk))
    # centre mark: V notch in the top edge above the "0" notch
    p = p.cut(cq.Workplane("XY").polyline([(-1.3, h["W"] + 0.01), (1.3, h["W"] + 0.01), (0, h["W"] - 1.4)])
              .close().extrude(h["T"] + 2).translate((0, 0, -1)))
    return p


def make_bumper():
    b = cq.Workplane("XY").circle(6.5).extrude(HANGER["T"]).faces(">Z").edges().chamfer(0.8)
    b = b.faces("<Z").edges().chamfer(0.3)
    b = b.cut(cyl(0, 0, -1, HANGER["T"] + 2, HANGER["screw_d"]))
    b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCone(HANGER["csk_d"] / 2 + 0.3, 0, HANGER["csk_d"] / 2 + 0.3,
                                                       pnt=cq.Vector(0, 0, -0.3), dir=cq.Vector(0, 0, 1))))
    return b


# --------------------------------------------------------------------------------------
FONT = None
for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]:
    if os.path.exists(f):
        FONT = f
        break

PARTS = {
    "tray": make_tray,
    "lid_board": make_lid_board,
    "lid_battery": make_lid_battery,
    "hanger": make_hanger,
    "bumper": make_bumper,
}

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for d in ("step", "stl"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    print(f"tray {X_R:.2f} x {Y_T:.2f} x {H:.1f} mm, board origin ({BX0:.2f},{BY0:.2f}), "
          f"battery x {BAT_X0:.2f}-{BAT_X1:.2f} y {Y_BAT0:.2f}-{Y_BAT1:.2f}")
    print(f"lead route {route_length():.1f} mm (available ~{BATT_LEAD - 6.0:.0f} mm of wire)")
    for name, fn in PARTS.items():
        s = fn()
        cq.exporters.export(s, os.path.join(root, "step", f"{name}.step"))
        cq.exporters.export(s, os.path.join(root, "stl", f"{name}.stl"), tolerance=0.01, angularTolerance=0.1)
        bb = s.val().BoundingBox()
        print(f"{name:12s} valid={s.val().isValid()} solids={len(s.solids().vals())} "
              f"bbox {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
