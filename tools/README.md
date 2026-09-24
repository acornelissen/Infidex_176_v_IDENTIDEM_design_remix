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
| `ct_pinion_teeth`, `ct_wheel1..4_teeth` | Tooth counts, sprocket end to dial end |
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

The sprocket and dial axes stay put; idler 3 is solved so it meshes with both idler 2 and the dial wheel. If a set of values cannot close, a gear would come within `ct_clearance` of the sprocket hub or the dial disc, or two stacked gears would come within `ct_axial_clearance` of each other, the script stops with a message instead of building. It does not know about the body walls or the cover bosses, so look at the gear bay yourself after a big change.

## Tests

`gearcalc.py` and `params.py` have no Fusion imports, so they can be tested with any Python:

```sh
pip install pytest shapely
pytest
```

64 tests cover the ratio, centre distances, the solved axis positions, radial and axial clash detection, the face heights and stepped bores of the built gears, the wall left under the pinion teeth, the tooth phases the model is drawn at, tooth geometry, the contact ratio of every mesh (at least 1.3 as drawn, and still 1.0 with the axes 0.2 mm apart), and that meshing outlines do not overlap through a full pitch.
