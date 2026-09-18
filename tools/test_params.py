import pytest
import gearcalc as gc
import params as pm


def test_defaults_rebuild_the_rev5_train():
    assert pm.to_spec(pm.default_values()) == gc.TrainSpec()


def test_every_default_has_a_fusion_unit_and_comment():
    for p in pm.PARAMETERS:
        assert p.unit in ("mm", "deg", "")
        assert p.comment


def test_parameter_names_are_unique_and_prefixed():
    names = [p.name for p in pm.PARAMETERS]
    assert len(names) == len(set(names))
    assert all(n.startswith("ct_") for n in names)


def test_changing_a_tooth_count_flows_into_the_spec():
    values = pm.default_values() | {"ct_wheel4_teeth": 40}
    assert pm.to_spec(values).wheel_teeth == (32, 30, 30, 40)


def test_teeth_are_rounded_to_whole_numbers():
    values = pm.default_values() | {"ct_pinion_teeth": 12.0000001}
    assert pm.to_spec(values).pinion_teeth == 12
