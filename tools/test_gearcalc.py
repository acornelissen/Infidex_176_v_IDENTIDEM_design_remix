import math
import pytest
import gearcalc as gc

TRAIN = gc.TrainSpec()   # defaults are the train as built in the CAD


def test_train_ratio_is_50_to_1():
    assert gc.ratio(TRAIN) == pytest.approx(50.0)


def test_centre_distances_match_rev5():
    assert [round(d, 2) for d in gc.centre_distances(TRAIN)] == [13.2, 12.6, 12.6, 14.4]


def test_layout_keeps_end_axes_and_meets_every_centre_distance():
    axes = gc.layout(TRAIN)
    assert axes[0] == pytest.approx(TRAIN.sprocket_axis)
    assert axes[-1] == pytest.approx(TRAIN.dial_axis)
    for (a, b), d in zip(zip(axes, axes[1:]), gc.centre_distances(TRAIN)):
        assert math.dist(a, b) == pytest.approx(d, abs=1e-9)


def test_layout_reproduces_rev5_idler_axes():
    rev5 = [(73.03, -58.41), (60.92, -61.88), (64.68, -49.86)]
    for got, want in zip(gc.layout(TRAIN)[1:4], rev5):
        assert math.dist(got, want) < 0.05


def test_unreachable_layout_raises():
    spec = gc.TrainSpec(wheel_teeth=(32, 30, 30, 80))
    with pytest.raises(gc.LayoutError):
        gc.layout(spec)


def test_train_layout_has_no_collisions():
    assert gc.collisions(TRAIN) == []


def test_collision_is_reported_when_a_wheel_hits_the_sprocket_hub():
    spec = gc.TrainSpec(idler2_angle_deg=90.0)
    assert gc.collisions(spec)


def test_profile_has_one_lobe_per_tooth_and_expected_diameters():
    g = gc.GearSpec(teeth=30, module=0.6)
    pts = gc.profile(g)
    radii = [math.hypot(x, y) for x, y in pts]
    assert max(radii) * 2 == pytest.approx(gc.tip_diameter(g), abs=0.02)
    assert min(radii) * 2 == pytest.approx(gc.root_diameter(g), abs=0.02)
    tip = gc.tip_diameter(g) / 2 - 0.01
    crossings = sum(1 for a, b in zip(radii, radii[1:] + radii[:1]) if a < tip <= b)
    assert crossings == 30


def test_tooth_thickness_at_pitch_circle_includes_backlash_thinning():
    g = gc.GearSpec(teeth=30, module=0.6, thinning=0.125)
    assert gc.tooth_thickness_at_pitch(g) == pytest.approx(math.pi * 0.6 / 2 - 0.125, abs=0.01)


def test_backlash_is_sum_of_thinning():
    assert gc.backlash(TRAIN, stage=0) == pytest.approx(0.20, abs=1e-6)


@pytest.mark.parametrize("gear, tip, root", [
    (lambda t: t.pinion(), 8.68, 6.17),
    (lambda t: t.wheel(0), 19.84, 17.21),
    (lambda t: t.wheel(1), 18.64, 16.01),
    (lambda t: t.wheel(3), 22.25, 19.61),
])
def test_train_diameters(gear, tip, root):
    g = gear(TRAIN)
    assert gc.tip_diameter(g) == pytest.approx(tip, abs=0.03)
    assert gc.root_diameter(g) == pytest.approx(root, abs=0.03)


def test_profile_shift_thickens_the_pinion_tooth():
    g = gc.GearSpec(teeth=12, module=0.6, shift=0.4, thinning=0.125)
    expected = math.pi * 0.6 / 2 + 2 * 0.4 * 0.6 * math.tan(math.radians(20)) - 0.125
    assert gc.tooth_thickness_at_pitch(g) == pytest.approx(expected, abs=0.01)


def test_train_tip_to_root_clearance_is_positive_on_every_mesh():
    for stage in range(4):
        assert gc.tip_root_clearance(TRAIN, stage) > 0.1


@pytest.mark.parametrize("stage", [None, 0, 1, 2, 3])
def test_train_outlines_are_simple_closed_polygons(stage):
    from shapely.geometry import Polygon
    g = TRAIN.pinion() if stage is None else TRAIN.wheel(stage)
    assert Polygon(gc.profile(g)).is_valid


@pytest.mark.parametrize("stage", range(4))
def test_meshing_outlines_do_not_overlap_at_any_phase(stage):
    from shapely.geometry import Polygon
    from shapely import affinity
    p, w = TRAIN.pinion(), TRAIN.wheel(stage)
    c = gc.centre_distances(TRAIN)[stage]
    pin = Polygon(gc.profile(p))
    for k in range(12):
        a = k * (360 / 12) / 6           # sweep one pinion pitch in 6 steps
        pp = affinity.rotate(pin, a, origin=(0, 0))
        # wheel turns the other way at the ratio, tooth space facing the pinion
        ww = affinity.rotate(Polygon(gc.profile(w)), 180 + 180 / w.teeth - a * p.teeth / w.teeth, origin=(0, 0))
        ww = affinity.translate(ww, c, 0)
        assert pp.intersection(ww).area < 1e-4


@pytest.mark.parametrize("stage", range(4))
def test_every_mesh_has_a_contact_ratio_of_at_least_1_3(stage):
    assert gc.contact_ratio(TRAIN, stage) >= 1.3


@pytest.mark.parametrize("stage", range(4))
def test_every_mesh_stays_in_contact_with_its_axes_0_2_mm_apart(stage):
    assert gc.contact_ratio(TRAIN, stage, spread=0.2) >= 1.0


def test_contact_ratio_falls_as_the_axes_spread():
    assert gc.contact_ratio(TRAIN, 3, spread=0.1) < gc.contact_ratio(TRAIN, 3)


def test_contact_ratio_of_a_standard_20_degree_pair():
    # 12/36 teeth, module 1, no shift or shaves: 1.56 from the textbook formula
    t = gc.TrainSpec(module=1.0, wheel_teeth=(32, 30, 30, 36), thinning=0.0, pinion_shift=0.0,
                     pinion_tip_reduction=0.0, wheel_tip_reduction=0.0)
    assert gc.contact_ratio(t, 3) == pytest.approx(1.56, abs=0.01)
