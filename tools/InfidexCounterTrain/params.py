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
    Param("ct_pinion0_z0", "mm", _D.pinion0_span[0], "Counter train: sprocket pinion underside"),
    Param("ct_pinion0_z1", "mm", _D.pinion0_span[1], "Counter train: sprocket pinion top"),
    Param("ct_wheel1_z0", "mm", _D.wheel_spans[0][0], "Counter train: idler 1 wheel underside"),
    Param("ct_wheel1_z1", "mm", _D.wheel_spans[0][1], "Counter train: idler 1 wheel top"),
    Param("ct_wheel2_z0", "mm", _D.wheel_spans[1][0], "Counter train: idler 2 wheel underside"),
    Param("ct_wheel2_z1", "mm", _D.wheel_spans[1][1], "Counter train: idler 2 wheel top"),
    Param("ct_wheel3_z0", "mm", _D.wheel_spans[2][0], "Counter train: idler 3 wheel underside"),
    Param("ct_wheel3_z1", "mm", _D.wheel_spans[2][1], "Counter train: idler 3 wheel top"),
    Param("ct_wheel4_z0", "mm", _D.wheel_spans[3][0], "Counter train: dial wheel underside"),
    Param("ct_wheel4_z1", "mm", _D.wheel_spans[3][1], "Counter train: dial wheel top"),
    Param("ct_pinion1_z1", "mm", _D.pinion_tops[0], "Counter train: idler 1 pinion top (starts at its wheel top)"),
    Param("ct_pinion2_z1", "mm", _D.pinion_tops[1], "Counter train: idler 2 pinion top (starts at its wheel top)"),
    Param("ct_pinion3_z1", "mm", _D.pinion_tops[2], "Counter train: idler 3 pinion top (starts at its wheel top)"),
    Param("ct_pinion_phase", "deg", _D.pinion_phase_deg, "Counter train: sprocket pinion tooth phase (others follow)"),
    Param("ct_clearance", "mm", _D.clearance, "Counter train: minimum radial gap to non-meshing parts"),
    Param("ct_axial_clearance", "mm", _D.axial_clearance, "Counter train: minimum axial gap between stacked gears"),
    Param("ct_bore1", "mm", _D.bores[0][0], "Counter train: idler 1 bore below the step"),
    Param("ct_bore1_upper", "mm", _D.bores[0][1], "Counter train: idler 1 bore above the step"),
    Param("ct_bore1_step_z", "mm", _D.bores[0][2], "Counter train: idler 1 bore step height"),
    Param("ct_bore2", "mm", _D.bores[1][0], "Counter train: idler 2 bore below the step"),
    Param("ct_bore2_upper", "mm", _D.bores[1][1], "Counter train: idler 2 bore above the step"),
    Param("ct_bore2_step_z", "mm", _D.bores[1][2], "Counter train: idler 2 bore step height"),
    Param("ct_bore3", "mm", _D.bores[2][0], "Counter train: idler 3 bore below the step"),
    Param("ct_bore3_upper", "mm", _D.bores[2][1], "Counter train: idler 3 bore above the step"),
    Param("ct_bore3_step_z", "mm", _D.bores[2][2], "Counter train: idler 3 bore step height"),
    Param("ct_bore4", "mm", _D.bores[3][0], "Counter train: dial wheel bore below the step"),
    Param("ct_bore4_upper", "mm", _D.bores[3][1], "Counter train: dial wheel bore above the step"),
    Param("ct_bore4_step_z", "mm", _D.bores[3][2], "Counter train: dial wheel bore step height"),
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
        pinion0_span=(v["ct_pinion0_z0"], v["ct_pinion0_z1"]),
        wheel_spans=tuple((v[f"ct_wheel{i}_z0"], v[f"ct_wheel{i}_z1"]) for i in range(1, 5)),
        pinion_tops=tuple(v[f"ct_pinion{i}_z1"] for i in range(1, 4)),
        bores=tuple((v[f"ct_bore{i}"], v[f"ct_bore{i}_upper"], v[f"ct_bore{i}_step_z"]) for i in range(1, 5)),
        pinion_phase_deg=v["ct_pinion_phase"],
        clearance=v["ct_clearance"],
        axial_clearance=v["ct_axial_clearance"],
    )
