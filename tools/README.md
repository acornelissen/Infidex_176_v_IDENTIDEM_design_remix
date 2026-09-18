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
2. Run **InfidexCounterTrain**. The first run creates the `ct_*` user parameters with the values of the train in this repository and builds the gears.
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
| `ct_face_width`, `ct_layer_gap`, `ct_base_z` | Gear thickness and stacking |
| `ct_bore1..4` | Bores |
| `ct_clearance` | Minimum gap to non-meshing parts |

The sprocket and dial axes stay put; idler 3 is solved so it meshes with both idler 2 and the dial wheel. If a set of values cannot close, or a gear would come within `ct_clearance` of the sprocket hub or the dial disc, the script stops with a message instead of building. It does not know about the body walls or the cover bosses, so look at the gear bay yourself after a big change.

## Tests

`gearcalc.py` and `params.py` have no Fusion imports, so they can be tested with any Python:

```sh
pip install pytest shapely
pytest
```

27 tests cover the ratio, centre distances, the solved axis positions, clash detection, tooth geometry, and that meshing outlines do not overlap through a full pitch.
