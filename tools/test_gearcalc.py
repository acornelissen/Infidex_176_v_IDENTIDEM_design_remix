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


# ---------- the train as built: face heights, bores and tooth phases ----------

BUILT_LAYERS = [(0, "pinion", 36.8, 40.8),
                (1, "wheel", 36.8, 38.5), (1, "pinion", 38.5, 40.8),
                (2, "wheel", 39.0, 40.8), (2, "pinion", 40.8, 43.0),
                (3, "wheel", 41.2, 43.0), (3, "pinion", 43.0, 45.4),
                (4, "wheel", 43.4, 45.9)]


def _span(axis, kind, spec=TRAIN):
    return next((z0, z1) for a, k, g, z0, z1 in gc.layers(spec) if a == axis and k == kind)


def test_layers_reproduce_the_built_stack():
    got = [(a, k, round(z0, 3), round(z1, 3)) for a, k, g, z0, z1 in gc.layers(TRAIN)]
    assert got == BUILT_LAYERS


@pytest.mark.parametrize("axis", [1, 2, 3])
def test_every_idler_is_one_continuous_body(axis):
    assert _span(axis, "wheel")[1] == pytest.approx(_span(axis, "pinion")[0])


@pytest.mark.parametrize("stage", range(4))
def test_meshing_faces_overlap_by_at_least_1_7_mm(stage):
    p0, p1 = _span(stage, "pinion")
    w0, w1 = _span(stage + 1, "wheel")
    assert min(p1, w1) - max(p0, w0) >= 1.7 - 1e-9


def test_axial_clash_is_reported_when_stacked_gears_come_too_close():
    import dataclasses
    spans = list(TRAIN.wheel_spans)
    spans[1] = (38.6, spans[1][1])          # idler 2's wheel 0.1 mm above idler 1's
    spec = dataclasses.replace(TRAIN, wheel_spans=tuple(spans))
    assert any({a, b} == {1, 2} for a, _, b, _, _ in gc.collisions(spec))


@pytest.mark.parametrize("axis, want", [
    (0, []),
    (1, [(4.4, 36.8, 38.8), (3.6, 38.8, 40.8)]),
    (2, [(3.61, 39.0, 43.0)]),
    (3, [(3.6, 41.2, 45.4)]),
    (4, [(3.2, 43.4, 45.9)]),
])
def test_bore_segments_match_the_built_gears(axis, want):
    got = gc.bore_segments(TRAIN, axis)
    assert len(got) == len(want)
    for g, w in zip(got, want):
        assert g == pytest.approx(w)


@pytest.mark.parametrize("axis", [1, 2, 3])
def test_bores_leave_at_least_0_8_mm_of_wall_under_the_pinion_teeth(axis):
    p0, p1 = _span(axis, "pinion")
    root_r = gc.root_diameter(TRAIN.pinion()) / 2
    for d, z0, z1 in gc.bore_segments(TRAIN, axis):
        if min(z1, p1) > max(z0, p0):
            assert root_r - d / 2 >= 0.8


def test_pinions_are_drawn_at_the_built_phase():
    ph = gc.phases(TRAIN)
    assert [ph[a]["pinion"] for a in range(4)] == pytest.approx([15.0] * 4)


@pytest.mark.parametrize("stage", range(4))
def test_built_phases_mesh_without_overlap_with_the_backlash_centred(stage):
    from shapely.geometry import Polygon
    axes, ph = gc.layout(TRAIN), gc.phases(TRAIN)
    pin = Polygon(gc.placed_profile(TRAIN.pinion(), axes[stage], ph[stage]["pinion"]))
    whl = Polygon(gc.placed_profile(TRAIN.wheel(stage), axes[stage + 1], ph[stage + 1]["wheel"]))
    assert pin.intersection(whl).area < 1e-4
    assert pin.distance(whl) > 0.05           # clear of both flanks, not resting on one


def test_placed_profile_rotates_about_the_gear_centre_then_moves_it():
    g = TRAIN.pinion()
    pts = gc.placed_profile(g, (10.0, -5.0), 90.0)
    tip = max(pts, key=lambda p: p[1])
    assert tip[0] == pytest.approx(10.0, abs=0.2)          # tooth 0 now points along +Y
    assert tip[1] == pytest.approx(-5.0 + gc.tip_diameter(g) / 2, abs=0.01)
    assert len(pts) == len(gc.profile(g))
