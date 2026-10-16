# CAD source

Parametric [CadQuery](https://cadquery.readthedocs.io/) model of the case, lids, hangers and bumpers. Licensed under MIT (see `../LICENSE-MIT`). The parts it generates are licensed under CC BY-SA 4.0.

| File | What it does |
|---|---|
| `ee02_frame_case.py` | The model. Parameters at the top; `python3 ee02_frame_case.py` writes `../step` and `../stl` |
| `build.py` | Writes STEP, STL and the Bambu Lab P1S plate `../print/ee02_case_P1S_plate.3mf` |
| `context.py` | Simplified board, battery, display, flex and frame geometry for the fit checks |
| `check_fit.py` | Checks for collisions with the board, battery and antenna, slides both lids through their full travel, and prints the battery lead route length |
| `diagrams.py` | Writes the dimensioned SVG drawings in `../docs/images` |

```sh
pip install -r requirements.txt   # cadquery, trimesh, numpy, manifold3d
python3 build.py
python3 check_fit.py
python3 diagrams.py
```

## Coordinates

The tray origin is its outer lower-left corner, seen from the **back** of the frame with the frame lying face down and the flex edge at the bottom.

- X points right, towards the frame's side rebate.
- Y points up, towards the display centre.
- Z points away from the passepartout.

Board-local coordinates `u`/`v` follow Seeed's KiCad file, and `B(u, v)` converts them to tray coordinates.

## Parameters worth knowing

| Parameter | Default | Meaning |
|---|---|---|
| `BATT_W`, `BATT_L`, `BATT_T` | 60.5, 91, 6.5 | Battery size; the pocket and the lead route follow it |
| `BATT_LEAD` | 62 | Lead length from cell to plug end; only used for the route check |
| `TAPE` | 1.0 | Foam tape thickness |
| `FIT` | 0.3 | Lid sliding clearance per side |
| `CLIP_C` | 0.25 | Vertical play between board and clip catch |
| `CLIP_O` | 1.4 | Catch depth; reaches `CLIP_O − CLIP_GAP` = 0.8 mm over the board |
| `CLR_FPC`, `CLR_BTN` | 0.8 | Board clearance to the lower and upper walls |
| `REBATE_CLR` | 2.0 | Gap between the case and the frame's rebate wall |
| `J1C_TO_REBATE` | 101.09 | Rebate distance from the flex tail centre, for a 300 mm wide passepartout with a centred 208.8 mm panel |
