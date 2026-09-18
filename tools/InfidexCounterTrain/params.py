"""Fusion user-parameter table for the counter train, and its mapping to TrainSpec.
Values here are in the display units (mm, deg, plain numbers)."""
from dataclasses import dataclass
import gearcalc as gc


@dataclass(frozen=True)
class Param:
    name: str
    unit: str
    value: float
    comment: str


_D = gc.TrainSpec()

PARAMETERS = (
    Param("ct_module", "mm", _D.module, "Counter train: gear module"),
    Param("ct_pressure_angle", "deg", _D.pressure_angle_deg, "Counter train: pressure angle"),
    Param("ct_pinion_teeth", "", _D.pinion_teeth, "Counter train: teeth on every pinion"),
    Param("ct_wheel1_teeth", "", _D.wheel_teeth[0], "Counter train: idler 1 wheel (meshes sprocket pinion)"),
    Param("ct_wheel2_teeth", "", _D.wheel_teeth[1], "Counter train: idler 2 wheel"),
    Param("ct_wheel3_teeth", "", _D.wheel_teeth[2], "Counter train: idler 3 wheel"),
    Param("ct_wheel4_teeth", "", _D.wheel_teeth[3], "Counter train: dial wheel"),
    Param("ct_thinning", "mm", _D.thinning, "Counter train: tooth thinning per gear (backlash share)"),
    Param("ct_pinion_shift", "", _D.pinion_shift, "Counter train: pinion profile shift x (wheels get -x)"),
    Param("ct_pinion_tip_reduction", "mm", _D.pinion_tip_reduction, "Counter train: pinion tip shave (radial)"),
    Param("ct_wheel_tip_reduction", "mm", _D.wheel_tip_reduction, "Counter train: wheel tip shave (radial)"),
    Param("ct_sprocket_x", "mm", _D.sprocket_axis[0], "Counter train: sprocket axis X (fixed)"),
    Param("ct_sprocket_y", "mm", _D.sprocket_axis[1], "Counter train: sprocket axis Y (fixed)"),
    Param("ct_dial_x", "mm", _D.dial_axis[0], "Counter train: dial axis X (fixed)"),
    Param("ct_dial_y", "mm", _D.dial_axis[1], "Counter train: dial axis Y (fixed)"),
    Param("ct_idler1_angle", "deg", _D.idler1_angle_deg, "Counter train: direction sprocket -> idler 1"),
    Param("ct_idler2_angle", "deg", _D.idler2_angle_deg, "Counter train: direction idler 1 -> idler 2"),
    Param("ct_idler3_elbow", "", _D.idler3_elbow, "Counter train: idler 3 solution, 1 or -1"),
    Param("ct_face_width", "mm", _D.face_width, "Counter train: gear face width"),
    Param("ct_layer_gap", "mm", _D.layer_gap, "Counter train: axial gap between gear layers"),
    Param("ct_base_z", "mm", _D.base_z, "Counter train: underside of idler 1 wheel"),
    Param("ct_clearance", "mm", _D.clearance, "Counter train: minimum gap to non-meshing parts"),
    Param("ct_bore1", "mm", _D.bores[0], "Counter train: idler 1 bore"),
    Param("ct_bore2", "mm", _D.bores[1], "Counter train: idler 2 bore"),
    Param("ct_bore3", "mm", _D.bores[2], "Counter train: idler 3 bore"),
    Param("ct_bore4", "mm", _D.bores[3], "Counter train: dial wheel bore"),
)


def default_values():
    return {p.name: p.value for p in PARAMETERS}


def to_spec(v):
    teeth = lambda k: int(round(v[k]))
    return gc.TrainSpec(
        module=v["ct_module"],
        pressure_angle_deg=v["ct_pressure_angle"],
        pinion_teeth=teeth("ct_pinion_teeth"),
        wheel_teeth=tuple(teeth(f"ct_wheel{i}_teeth") for i in range(1, 5)),
        thinning=v["ct_thinning"],
        pinion_shift=v["ct_pinion_shift"],
        pinion_tip_reduction=v["ct_pinion_tip_reduction"],
        wheel_tip_reduction=v["ct_wheel_tip_reduction"],
        sprocket_axis=(v["ct_sprocket_x"], v["ct_sprocket_y"]),
        dial_axis=(v["ct_dial_x"], v["ct_dial_y"]),
        idler1_angle_deg=v["ct_idler1_angle"],
        idler2_angle_deg=v["ct_idler2_angle"],
        idler3_elbow=1 if v["ct_idler3_elbow"] >= 0 else -1,
        face_width=v["ct_face_width"],
        layer_gap=v["ct_layer_gap"],
        base_z=v["ct_base_z"],
        clearance=v["ct_clearance"],
        bores=tuple(v[f"ct_bore{i}"] for i in range(1, 5)),
    )
