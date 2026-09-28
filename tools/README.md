# Counter train rebuild script

A Fusion script that builds the frame-counter gear train from a table of parameters, so a different reduction or module is a value edit and a rerun rather than a redraw.

## What is in here

| Path | What it is |
|---|---|
| `InfidexCounterTrain/InfidexCounterTrain.py` | The Fusion script: reads the parameters, validates the layout, draws and extrudes the gears |
| `InfidexCounterTrain/gearcalc.py` | The gear maths: ratios, centre distances, the solved idler axes, tooth profiles, clash checks. No Fusion imports |
| `InfidexCounterTrain/params.py` | The parameter table and its defaults |
| `test_gearcalc.py`, `test_params.py` | Tests, run outside Fusion |

## Install

1. In Fusion, press Shift+S to open Scripts and Add-Ins.
2. Click the **+** next to the script list, choose **Script or add-in from device**, and pick the `InfidexCounterTrain` folder from this repository.

Nothing needs installing into Fusion's Python. The script uses only the Fusion API and the two modules beside it.

## Use

1. Make a new **Hybrid Design** or **Assembly Design** document. Part Design only allows one component, so the script falls back to plain bodies there.
2. Run **InfidexCounterTrain**. The first run creates the `ct_*` user parameters with the values of the train in this repository and builds the gears. It also removes `ct_*` parameters left by older versions of the script.
3. Edit any value in **Modify > Change Parameters**, then run the script again. Fusion cannot drive involute tooth curves from parameters on its own, so a rerun is what rebuilds them. Each rebuild replaces the previous one as a single timeline group.

## Parameters

| Parameter | What it sets |
|---|---|
| `ct_module`, `ct_pressure_angle` | Gear module and pressure angle |
| `ct_pinion0..3_teeth`, `ct_wheel1..4_teeth` | Tooth counts, sprocket end to dial end. Pinion *n* drives wheel *n + 1* |
| `ct_thinning` | Tooth thinning per gear, which is the backlash share |
| `ct_pinion_shift` | Profile shift on the pinions; the wheels take the opposite |
| `ct_pinion_tip_reduction`, `ct_wheel_tip_reduction` | Tip shaves |
| `ct_sprocket_x/y`, `ct_dial_x/y` | The two fixed axes in the body |
| `ct_idler1_angle`, `ct_idler2_angle`, `ct_idler3_elbow` | Where the idlers sit |
| `ct_pinion0_z0/z1`, `ct_wheel1..4_z0/z1`, `ct_pinion1..3_z1` | Underside and top of every toothed layer; each idler pinion starts on top of its wheel |
| `ct_bore1..4`, `ct_bore1..4_upper`, `ct_bore1..4_step_z` | Bore below and above a step, and the step height; set both diameters equal for a plain bore |
| `ct_pinion_phase` | Tooth angle of the pinions; each wheel is turned to mesh with the pinion driving it |
| `ct_clearance` | Minimum radial gap to non-meshing parts |
| `ct_axial_clearance` | Minimum gap between gears that pass over each other |

Axis numbers and the part files they print as: idler 1 is `counter-coupling-gear`, idler 2 is `counter-idler-1`, idler 3 is `counter-idler-2` and the dial wheel is `counter-gear`. The built components carry both names.

### 20-frame train

Set `ct_pinion2_teeth` to 14 and `ct_wheel3_teeth` to 28, then rerun. Mesh 3 keeps its 12.6 mm centres, so every axis stays where it is and only idler 2 and idler 3 change. The train drops from 50:1 to 40:1, and the dial turns once per 20 frames instead of 25. The summary shows the frames per dial turn after every build.

The sprocket and dial axes stay put; idler 3 is solved so it meshes with both idler 2 and the dial wheel. If a set of values cannot close, a gear would come within `ct_clearance` of the sprocket hub or the dial disc, or two stacked gears would come within `ct_axial_clearance` of each other, the script stops with a message instead of building. It does not know about the body walls or the cover bosses, so look at the gear bay yourself after a big change.

## Tests

`gearcalc.py` and `params.py` have no Fusion imports, so they can be tested outside Fusion. From the repository root, with [mise](https://mise.jdx.dev):

```sh
mise run test
```

The tests cover the ratio and frames per dial turn, centre distances, the solved axis positions, radial and axial clash detection, the face heights and stepped bores of the built gears, the wall left under the pinion teeth, the tooth phases the model is drawn at, tooth geometry, the contact ratio of every mesh (at least 1.3 as drawn, and still 1.0 with the axes 0.2 mm apart), that meshing outlines do not overlap through a full pitch, and the same checks on the 20-frame train.

## CAD export and checks

`cad/` is a small Python package that keeps the 3MFs in step with the STEP (`cad/Infidex176V-IDENTIDEM.design-remix.step` at the repository root). Run it through mise from anywhere in the repository:

| Task | What it does |
|---|---|
| `mise run verify` | Checks every file in `3mf/parts/` and every object in the Bambu project. Each mesh must be closed, consistently wound and of positive volume; each part file must match the STEP solid of the same name within 0.02 mm RMS and 0.5 % volume; the inlay in a two-colour file must sit where the STEP puts it; each project object must match its part file. Every plate is checked too: each object inside its bed, clear of the bed's excluded corner, resting at z 0, and at least 6 mm from the other objects on the plate. Prints a table and exits non-zero on any failure. Add part names to check only those. Takes about two minutes |
| `mise run export -- <part names>` | Re-exports parts after a CAD change. For every mesh of the part (its part file, a two-colour file holding it, its project object) it fits the solid from the STEP as committed (`--ref`, default `HEAD`) onto the mesh, then writes the solid from the current STEP through the same transform, so each copy keeps its place on the bed. Everything else in the archives is copied byte for byte. If the old solid does not fit a mesh within 0.02 mm, nothing is written. Safe to run twice before committing: a mesh the current solid already fits better, within 0.001 mm, is reported as already exported and left alone. `--dry-run` reports without writing |
| `mise run add -- <solid> --like <sibling>` | Adds a solid that is new in the STEP, printed like a sibling part (`--like simple-counter-face` for a new face). Writes `3mf/parts/<solid>.3mf` in the sibling's layout, through the transform that fits the sibling's solid onto the sibling's mesh, so orientation and bed contact match. If the sibling has a two-colour file, give `--inlay <STEP solid>` and a `<solid>-two-colour.3mf` is written with the face, the inlay and the group (`--inlay counter-face-inlay` means the loose `Body1`, `Body2`, ... bodies; a new inlay is one named solid such as `counter-face-20-inlay`). In the project, the sibling's object is cloned (print settings, assembly place) and put at a free spot at least 6 mm from everything on the sibling's plate, or on `--plate <number or name>`. Nothing is written if a fit fails, the new part would not rest on the bed like the sibling, or the plate has no room. `--dry-run` reports without writing |
| `mise run plates -- list` | Lists the project's plates and their objects. `add-plate <name>` appends an empty plate, `rename-plate <plate> <name>` renames one, `move <object> <plate>` moves an object to a free spot on a plate. A plate is given by number or name |
| `mise run layout` | Gives each counter option its own plate: simple cover, drag cover, 25-frame idlers, simple and drag 25-frame faces, and, once `add` has made them, 20-frame idlers and simple and drag 20-frame faces. The shared counter gears stay on Small parts 2. Safe to rerun: existing plates are reused by name and parts already in place are left alone |
| `mise run clearance` | Checks the counter train against the housings and each other, as assembled in the STEP. Reports the shared volume and the smallest gap per pair, and fails on an overlap over 0.001 mm³. Alternatives, of which a camera has one, are never checked against each other: the covers (`simple-cover`, `drag-cover`), the idler sets (`counter-idler-1`/`-2` for 25 frames, `counter-idler-1-20`/`-2-20` for 20) and the counter faces. Each idler set is checked in its own train (`ratchet-coupling-gear`, `counter-coupling-gear`, idler 1, idler 2, `counter-gear`) and against `body-solid`, `body-top` and each cover; each face against each cover and `counter-gear`, which holds it. Meshing pairs, where a pinion drives the next wheel in the train, are reported but not judged; their teeth are the gear maths' job. Options not in the STEP yet are skipped with a note |

Workflow after changing the CAD: export the STEP from Fusion over the one in `cad/`, run `mise run export -- <changed parts>`, then `mise run verify` and, for the counter train, `mise run clearance`. Commit the STEP and the 3MFs together, so the next export fits against the right STEP.

Adding the 20-frame counter parts, once they are in the STEP:

```sh
mise run add -- simple-counter-face-20 --like simple-counter-face --inlay counter-face-20-inlay
mise run add -- drag-counter-face-20 --like drag-counter-face --inlay counter-face-20-inlay
mise run add -- counter-idler-1-20 --like counter-idler-1
mise run add -- counter-idler-2-20 --like counter-idler-2
mise run layout
mise run verify
mise run clearance
```

Then open the project in Bambu Studio, look over the plates and save it, which redraws the plate thumbnails.

Notes:

- The fit error is measured from the mesh's vertices to the STEP surface, because the vertices of an exported mesh lie on the true surface whatever the facet size. Nearly symmetric parts may come out turned about their own axis by a symmetry step; their footprint on the bed is the same.
- Part file names map to STEP solid names one to one, except `pressure-plate-1` (`pressure-plate (1)`) and the two-colour files, which hold the face and an inlay named after its STEP solid (`counter-face-inlay` stands for the STEP bodies `Body1`, `Body2`, and so on).
- `--step FILE` makes `verify`, `export`, `add` and `clearance` use another STEP, for example one taken from git. `verify` and `add` also take `--parts DIR` and `--project FILE`, to work on copies.
- Plates: Bambu Studio lays plates out in a grid with a stride of the bed size plus a fifth (307.2 mm for the 256 mm bed), and picks the column count from the plate count: the square root, rounded, plus one if the root is above its rounding (`compute_colum_count` in BambuStudio `src/slic3r/GUI/PartPlate.hpp`). It gives each object to the plate it sits on when it loads a project, so when adding a plate changes the column count (10 and 17 plates), `plates` and `layout` move every object with its plate. New plates have no thumbnails until Bambu Studio saves the project.
