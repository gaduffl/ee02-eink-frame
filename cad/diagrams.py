"""Dimensioned SVG diagrams for the docs, generated from the same parameters as the CAD.

SPDX-License-Identifier: MIT
Usage:  python3 diagrams.py   -> ../docs/images/back-view.svg, depth.svg, hanger.svg
"""
import math
import os
import re
import ee02_frame_case as M
import context as C

F = lambda v: (f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))

ANT_X0 = 258.0     # antenna position on the passepartout (frame coords, back view)
ANT_Y0 = 14.0


def back_view():
    body = C.PROF_W - C.LIP_W
    W, H = C.PP_W, C.PP_H
    Y = lambda y: H + body - y
    left, right, top, bot = 92, 122, 22, 44
    vb = (-body - left, -top, W + 2 * body + left + right, H + 2 * body + top + bot)
    s = []
    a = s.append
    a(f'<svg viewBox="{F(vb[0])} {F(vb[1])} {F(vb[2])} {F(vb[3])}" role="img" aria-labelledby="bvT bvD" class="dwg dwg-back">')
    a('<title id="bvT">Back view of the frame with the case in place</title>')
    a('<desc id="bvD">Frame lying face down. The display flex folds around the panel\'s lower edge. The L-shaped case sits over the panel\'s lower right corner and is taped to the passepartout\'s right margin; the battery sits above the EE02 board and its lid slides out towards the frame centre. Hangers on the top edge and left edge, bumpers in the corners.</desc>')
    a('<defs><pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
      '<line x1="0" y1="0" x2="0" y2="4" class="hatch"/></pattern>'
      '<marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
      '<path d="M0,0 L8,4 L0,8 z" class="arrowhead"/></marker></defs>')
    a(f'<path class="wood" fill-rule="evenodd" d="M{F(-body)},{F(Y(H+body))} h{F(W+2*body)} v{F(H+2*body)} h{F(-(W+2*body))} z '
      f'M0,{F(Y(H))} h{F(W)} v{F(H)} h{F(-W)} z"/>')
    a(f'<rect class="pp" x="0" y="{F(Y(H))}" width="{F(W)}" height="{F(H)}"/>')
    px, py, pw, ph = C.PANEL_X0, C.PANEL_Y0, C.PANEL_W, C.PANEL_H
    a(f'<rect class="panel" x="{F(px)}" y="{F(Y(py+ph))}" width="{F(pw)}" height="{F(ph)}"/>')
    a(f'<rect class="aa" x="{F(px+3)}" y="{F(Y(py+ph-3))}" width="{F(pw-6)}" height="{F(C.AA_H)}"/>')
    a(f'<text class="lbl onpanel" x="{F(px+pw/2)}" y="{F(Y(py+ph/2))}" text-anchor="middle">display, back side</text>')
    a(f'<text class="lbl onpanel small" x="{F(px+pw/2)}" y="{F(Y(py+ph/2)+13)}" text-anchor="middle">208.8 × 284.7</text>')
    wide_top = py + C.FPC_WIDE_LEN - math.pi * C.FOLD_R
    a(f'<rect class="flex" x="{F(C.WIDE_X[0])}" y="{F(Y(wide_top))}" width="{F(C.WIDE_X[1]-C.WIDE_X[0])}" height="{F(wide_top-py)}"/>')
    tail_top = C.tail_end_y
    a(f'<rect class="flex" x="{F(C.TAIL_X[0])}" y="{F(Y(tail_top))}" width="{F(C.TAIL_X[1]-C.TAIL_X[0])}" height="{F(tail_top-wide_top)}"/>')
    a(f'<path class="foldmark" d="M{F(C.WIDE_X[0])},{F(Y(py))} h{F(C.WIDE_X[1]-C.WIDE_X[0])}"/>')
    tx, ty = C.TRAY_X, C.TRAY_Y
    # battery lid slid out (dashed): the space it needs above the case
    sl = M.Y_T - M.WALL_D - M.FIT
    a(f'<rect class="slidepath" x="{F(tx+M.X_CO)}" y="{F(Y(ty+M.Y_T+sl))}" width="{F(M.X_R-M.X_CO)}" height="{F(sl)}" rx="2.5"/>')
    a(f'<path class="slidearrow" d="M{F(tx+(M.X_CO+M.X_R)/2)},{F(Y(ty+M.Y_T+8))} V{F(Y(ty+M.Y_T+46))}" marker-end="url(#ar)"/>')
    pts = [(0, 0), (M.X_R, 0), (M.X_R, M.Y_T), (M.X_CO, M.Y_T), (M.X_CO, M.Y_BS), (0, M.Y_BS)]
    d = "M" + " L".join(f"{F(tx+x)},{F(Y(ty+y))}" for x, y in pts) + " Z"
    a(f'<path class="case" d="{d}"/>')
    tz0 = C.PANEL_X0 + C.PANEL_W + 2
    a(f'<rect class="tape" x="{F(tz0)}" y="{F(Y(ty+M.Y_T-3))}" width="{F(tx+M.X_R-2-tz0)}" height="{F(M.Y_T-6)}"/>')
    bx0, by0 = tx + M.BX0, ty + M.BY0
    a(f'<rect class="pcb" x="{F(bx0)}" y="{F(Y(by0+M.PCB_W))}" width="{F(M.PCB_L)}" height="{F(M.PCB_W)}" rx="2"/>')
    a(f'<rect class="batt" x="{F(tx+M.BAT_X0)}" y="{F(Y(ty+M.Y_BAT1))}" width="{F(M.BATT_W)}" height="{F(M.BATT_L)}" rx="2"/>')
    kx0 = tx + M.B(M.KEY_OPEN_U[0], 0)[0]
    a(f'<rect class="keyopen" x="{F(kx0)}" y="{F(Y(ty+M.Y_BS+0.2))}" width="{F(M.KEY_OPEN_U[1]-M.KEY_OPEN_U[0])}" height="3"/>')
    route = M.lead_route()
    a('<path class="leads" d="M' + " L".join(f"{F(tx+x)},{F(Y(ty+y))}" for x, y, _ in route) + '"/>')
    hole_x = tx + M.B(M.UFL[0] + 2.5, 0)[0]
    a(f'<rect class="ant" x="{F(ANT_X0)}" y="{F(Y(ANT_Y0+38))}" width="22" height="38"/>')
    a(f'<path class="cable" d="M{F(hole_x)},{F(Y(ty))} C{F(hole_x)},{F(Y(ty-12))} {F(ANT_X0+8)},{F(Y(ANT_Y0+52))} {F(ANT_X0+8)},{F(Y(ANT_Y0+36))}"/>')
    hL, hW = M.HANGER["L"], M.HANGER["W"]
    a(f'<rect class="hanger" x="{F(W/2-hL/2)}" y="{F(Y(H+body-0.5))}" width="{F(hL)}" height="{F(hW)}" rx="3"/>')
    a(f'<rect class="hanger" x="{F(-body+0.5)}" y="{F(Y(H/2+hL/2))}" width="{F(hW)}" height="{F(hL)}" rx="3"/>')
    for (cx, cy) in [(-body/2, -body/2), (W+body/2, -body/2), (-body/2, H+body/2), (W+body/2, H+body/2)]:
        a(f'<circle class="bumper" cx="{F(cx)}" cy="{F(Y(cy))}" r="6.5"/>')

    def dim_h(x0, x1, y, text, above=True):
        yy = Y(y)
        a(f'<path class="dim" d="M{F(x0)},{F(yy)} H{F(x1)}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
        a(f'<text class="dimt" x="{F((x0+x1)/2)}" y="{F(yy-3 if above else yy+10)}" text-anchor="middle">{text}</text>')

    def dim_v(x, y0, y1, text, right=True):
        a(f'<path class="dim" d="M{F(x)},{F(Y(y0))} V{F(Y(y1))}" marker-start="url(#ar)" marker-end="url(#ar)"/>')
        a(f'<text class="dimt" x="{F(x+3 if right else x-3)}" y="{F((Y(y0)+Y(y1))/2+3)}" text-anchor="{"start" if right else "end"}">{text}</text>')

    dim_h(px + pw, W, 368, "45.6")
    dim_v(22, 0, py, "53.5")
    dim_h(tx, tx + M.X_R, ty - 12, F(round(M.X_R, 1)), above=False)
    dim_v(tx + M.X_R + 6, ty, ty + M.Y_T, F(round(M.Y_T, 1)))

    def call(x, y, lx, ly, lines, side="right"):
        a(f'<path class="leader" d="M{F(x)},{F(Y(y))} L{F(lx)},{F(Y(ly))}"/>')
        anc = "start" if side == "right" else "end"
        dx = 3 if side == "right" else -3
        for i, t in enumerate(lines):
            a(f'<text class="lbl" x="{F(lx+dx)}" y="{F(Y(ly)+3.5+i*11)}" text-anchor="{anc}">{t}</text>')

    R = W + body + 10
    Lx = -body - 10
    call(W / 2 + hL / 2, H + body - 7, R, H + 2, ["hanger,", "portrait"])
    call(tx + M.X_R - 4, ty + M.Y_T + sl - 20, R, ty + M.Y_T + sl - 6, ["battery lid", "slides out", "to here"])
    call(tx + M.BAT_X0 + 18, ty + M.Y_BAT0 + 60, R, ty + M.Y_T - 10, ["battery"])
    call(tx + 30, ty + 20, Lx, 150, ["EE02 board"], side="left")
    call(kx0 + 6, ty + M.Y_BS + 1.5, Lx, 205, ["keys + switch", "opening"], side="left")
    call(tx + M.X_R - 10, ty + 14, R, ty - 4, ["tape here"])
    call(ANT_X0 + 22, ANT_Y0 + 20, R, ANT_Y0 + 22, ["antenna"])
    call(W + body / 2 + 4, -body / 2 - 3, R, -body + 2, ["bumper ×4"])
    call(-body + 7, H / 2 + hL / 2 - 3, Lx, H / 2 + hL / 2 + 28, ["hanger,", "landscape"], side="left")
    call(C.WIDE_X[0] + 3, py + 7, Lx, py + 40, ["flex folded", "180° here"], side="left")
    a(f'<text class="cap" x="{F(W/2)}" y="{F(Y(-body)+30)}" text-anchor="middle">BACK VIEW · FRAME FACE DOWN · MM</text>')
    a('</svg>')
    return "\n".join(s)


def depth_stack():
    k = 5.0
    body = C.PROF_W - C.LIP_W
    g, pp, tape, h = C.GLASS_T, C.PP_T, M.TAPE, M.H
    lip, depth = C.LIP_T, C.PROF_D
    avail = depth - lip - g - pp
    gap = 300 - (C.TRAY_X + M.X_R)
    xe = 46.0
    x_min, x_max = -body - 19.0, xe + 40.0
    S = lambda v: F(v * k)
    s = []
    a = s.append
    a(f'<svg viewBox="{S(x_min)} {S(-3)} {S(x_max-x_min)} {S(depth+12)}" role="img" aria-labelledby="dsT dsD" class="dwg dwg-depth">')
    a('<title id="dsT">Depth stack next to the case</title>')
    a(f'<desc id="dsD">Section through the frame edge beside the case. Frame profile 30 mm deep with a {F(lip)} mm lip. Behind it: glass {F(g)} mm (assumed), passepartout {F(pp)} mm, foam tape {F(tape)} mm, case {F(h)} mm. About {F(avail)} mm is available behind the passepartout.</desc>')
    a('<defs><marker id="ar2" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L8,4 L0,8 z" class="arrowhead"/></marker></defs>')
    a(f'<path class="wood" d="M{S(-body)},0 H{S(C.LIP_W)} V{S(lip)} H0 V{S(depth)} H{S(-body)} Z"/>')
    y = lip
    layers = []
    a(f'<rect class="glass" x="0" y="{S(y)}" width="{S(xe)}" height="{S(g)}"/>'); layers.append((y + g / 2, f"glass {F(g)} (assumed)")); y += g
    a(f'<rect class="pp" x="0" y="{S(y)}" width="{S(xe)}" height="{S(pp)}"/>'); layers.append((y + pp / 2, f"passepartout {F(pp)}")); y += pp
    y_pp_back = y
    a(f'<rect class="tapeband" x="{S(gap+2)}" y="{S(y)}" width="{S(xe-gap-2)}" height="{S(tape)}"/>'); layers.append((y + tape / 2, f"foam tape {F(tape)}")); yt = y; y += tape
    a(f'<rect class="case" x="{S(gap)}" y="{S(y)}" width="{S(xe-gap)}" height="{S(h)}"/>')
    bx = gap + (M.X_R - M.BAT_X1)
    a(f'<rect class="batt" x="{S(bx)}" y="{S(y+M.Z_RIB)}" width="{S(xe-bx+3)}" height="{S(M.BATT_T)}" rx="{S(1.2)}"/>')
    a(f'<rect class="lidband" x="{S(gap+2)}" y="{S(y+M.Z_LID)}" width="{S(xe-gap-2)}" height="{S(M.LID_T)}"/>')
    layers.append((y + h / 2, f"case {F(h)}")); yc = y; y += h
    a(f'<path class="backplane" d="M{S(-body)},{S(depth)} H{S(xe)}"/>')
    layers.append((depth, "back of frame"))
    for (yy, t), yl in zip(layers, [2.4, 8.2, 14.0, 20.5, 29.6]):
        a(f'<path class="leader" d="M{S(xe)},{S(yy)} L{S(xe+5)},{S(yl)} H{S(xe+7)}"/>')
        a(f'<text class="lbl" x="{S(xe+8)}" y="{F(yl*k+4)}">{t}</text>')

    def dv(x, y0, y1, t):
        a(f'<path class="dim" d="M{S(x)},{S(y0)} V{S(y1)}" marker-start="url(#ar2)" marker-end="url(#ar2)"/>')
        a(f'<text class="dimt" x="{F(x*k-5)}" y="{F((y0+y1)/2*k+4)}" text-anchor="end">{t}</text>')
    dv(-body - 2.5, 0, depth, "30")
    dv(-body - 11.5, y_pp_back, depth, F(avail))
    dv(gap + 38, yt, yc + h, F(tape + h))
    a(f'<text class="dimt" x="{S(gap/2)}" y="{S(depth+6.5)}" text-anchor="middle">{F(round(gap,1))} to rebate</text>')
    a(f'<path class="leader" d="M{S(gap/2)},{S(depth+4.2)} V{S(yc+h+0.6)}"/>')
    a('</svg>')
    return "\n".join(s)


def hanger_diagram():
    h = M.HANGER
    k = 5.0
    L, Wd = h["L"], h["W"]
    S = lambda v: F(v * k)
    Y = lambda y: Wd - y
    s = []
    a = s.append
    a(f'<svg viewBox="{S(-L/2-3)} {S(-3)} {S(L+6)} {S(Wd+12)}" role="img" aria-labelledby="hgT hgD" class="dwg dwg-hanger">')
    a('<title id="hgT">Wall hanger, wall side</title>')
    a('<desc id="hgD">Keyhole slot with seven notches 4 mm apart. Push the screw head through the round hole, slide sideways, and let it drop into a notch. The V mark on the top edge is the centre notch.</desc>')
    a('<defs><marker id="ar3" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L8,4 L0,8 z" class="arrowhead accent"/></marker></defs>')
    a(f'<rect class="hangerplate" x="{S(-L/2)}" y="0" width="{S(L)}" height="{S(Wd)}" rx="{S(3)}"/>')
    a(f'<rect class="slot" x="{S(h["slot_x0"])}" y="{S(Y(h["slot_y1"]))}" width="{S(h["slot_x1"]-h["slot_x0"])}" height="{S(h["slot_y1"]-h["slot_y0"])}"/>')
    for nx in h["notch_x"]:
        a(f'<circle class="slot" cx="{S(nx)}" cy="{S(Y(h["seat_y"]))}" r="{S(h["seat_r"])}"/>')
    ex, ey, ed = h["entry"]
    a(f'<circle class="slot" cx="{S(ex)}" cy="{S(Y(ey))}" r="{S(ed/2)}"/>')
    for sx in h["screws"]:
        a(f'<circle class="csk" cx="{S(sx)}" cy="{S(Y(Wd/2))}" r="{S(h["csk_d"]/2)}"/><circle class="slot" cx="{S(sx)}" cy="{S(Y(Wd/2))}" r="{S(h["screw_d"]/2)}"/>')
    a(f'<path class="vmark" d="M{S(-1.4)},0 L{S(1.4)},0 L0,{S(1.5)} Z"/>')
    a(f'<circle class="screw" cx="{S(4)}" cy="{S(Y(h["seat_y"]))}" r="{S(2)}"/>')
    a(f'<path class="move" d="M{S(ex)},{S(Y(ey)+5.6)} C{S(ex+6)},{S(Y(ey)+9)} {S(-2)},{S(Y(ey)+9)} {S(3)},{S(Y(h["seat_y"])+2.6)}" marker-end="url(#ar3)"/>')
    a(f'<text class="dimt" x="0" y="{S(Wd+7.2)}" text-anchor="middle">7 notches, 4 mm apart · screw head up to 8.4 mm</text>')
    a('</svg>')
    return "\n".join(s)


STYLE = """
.dwg text{font-family:Helvetica, Arial, sans-serif}
.dwg .wood{fill:#C49A6C; stroke:#7A5634; stroke-width:.6}
.dwg .pp{fill:#F3F2EC; stroke:#A3A6A2; stroke-width:.4}
.dwg .panel{fill:#7C838B}
.dwg .aa{fill:none; stroke:#FFFFFF; stroke-width:.6; stroke-dasharray:4 3; opacity:.8}
.dwg .flex{fill:#D5842A}
.dwg .foldmark{stroke:#7A4A10; stroke-width:1.8}
.dwg .case{fill:#2F58C9; fill-opacity:.2; stroke:#2F58C9; stroke-width:1.2}
.dwg .tape{fill:url(#hatch)}
.dwg .hatch{stroke:#2F58C9; stroke-width:1}
.dwg .pcb{fill:#1D2320; fill-opacity:.88}
.dwg .batt{fill:#A5ACB6; stroke:#2B3136; stroke-width:.4}
.dwg .ant{fill:#1E2023}
.dwg .cable{stroke:#1E2023; stroke-width:1; fill:none}
.dwg .window{fill:none; stroke:#C23A30; stroke-width:.9; stroke-dasharray:3 2}
.dwg .slidepath{fill:#E8EDF1; fill-opacity:.35; stroke:#2F58C9; stroke-width:.9; stroke-dasharray:4 3}
.dwg .slidearrow{stroke:#2F58C9; stroke-width:1.6; fill:none}
.dwg .keyopen{fill:#C23A30}
.dwg .leads{stroke:#C23A30; stroke-width:1.4; fill:none; stroke-linejoin:round}
.dwg .hanger,.dwg .bumper,.dwg .hangerplate{fill:#2F58C9}
.dwg .dim{stroke:#2B3136; stroke-width:.6; fill:none}
.dwg .arrowhead{fill:#2B3136}
.dwg .arrowhead.accent{fill:#C23A30}
.dwg .dimt{font:500 9.5px Menlo, Consolas, "DejaVu Sans Mono", monospace; fill:#2B3136}
.dwg .lbl{font-size:10.5px; fill:#14181B}
.dwg .onpanel{fill:#FFFFFF}
.dwg .small{font:500 8.5px Menlo, Consolas, "DejaVu Sans Mono", monospace}
.dwg .leader{stroke:#6B757D; stroke-width:.5; fill:none}
.dwg .cap{font:500 9px Menlo, Consolas, "DejaVu Sans Mono", monospace; letter-spacing:.14em; fill:#55606A}
.dwg-depth .lbl{font-size:13.5px}
.dwg-depth .dimt{font-size:12.5px}
.dwg .glass{fill:#CFE2EA; stroke:#2B3136; stroke-width:.3; opacity:.9}
.dwg .tapeband{fill:#E0AE10}
.dwg .lidband{fill:#E8EDF1; stroke:#2F58C9; stroke-width:.8}
.dwg .backplane{stroke:#C23A30; stroke-width:1.2; stroke-dasharray:5 3}
.dwg-hanger .dimt{font-size:13px}
.dwg .slot{fill:#F7F9F8}
.dwg .csk{fill:none; stroke:#F7F9F8; stroke-width:1.5}
.dwg .vmark{fill:#F7F9F8}
.dwg .screw{fill:#C23A30}
.dwg .move{stroke:#C23A30; stroke-width:2; fill:none}
.dwg{background:#F7F9F8}
"""


def standalone(svg):
    """make an inline page drawing a self-contained SVG file (light colours, own background)"""
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    svg = svg.replace("<svg ", f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb[2] * 2:.0f}" height="{vb[3] * 2:.0f}" ', 1)
    head, rest = svg.split(">", 1)
    bg = f'<rect x="{vb[0]:.2f}" y="{vb[1]:.2f}" width="{vb[2]:.2f}" height="{vb[3]:.2f}" fill="#F7F9F8"/>'
    return f"{head}><style>{STYLE}</style>{bg}{rest}"


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "images")
    os.makedirs(out, exist_ok=True)
    for n, f in [("back-view", back_view), ("depth", depth_stack), ("hanger", hanger_diagram)]:
        with open(os.path.join(out, f"{n}.svg"), "w") as fh:
            fh.write(standalone(f()))
    print("wrote", out)
