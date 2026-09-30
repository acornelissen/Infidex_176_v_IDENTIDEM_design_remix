import pytest
import trimesh

from cad import step, threemf
from cad.add import Refused, mesh_object, rename, two_colour_model
from test_cad_threemf import model


def test_rename_swaps_whole_names_and_the_title():
    xml = model((1, "simple-counter-face", trimesh.creation.box()), (2, "counter-face-inlay", trimesh.creation.box()))
    xml = xml.replace("<resources>", '<metadata name="Title">simple-counter-face-two-colour</metadata>\n <resources>')
    xml += '<object id="3" name="simple-counter-face-two-colour"/>'
    out = rename(xml, {"simple-counter-face": "simple-counter-face-b", "counter-face-inlay": "counter-face-b-inlay",
                       "simple-counter-face-two-colour": "simple-counter-face-b-two-colour"})
    assert [o["name"] for o in threemf.objects(out)] == ["simple-counter-face-b", "counter-face-b-inlay"]
    assert '<metadata name="Title">simple-counter-face-b-two-colour</metadata>' in out
    assert 'name="simple-counter-face-b-two-colour"' in out


def test_mesh_object_takes_the_named_mesh_or_the_only_one():
    box = trimesh.creation.box()
    assert mesh_object(model((1, "a", box), (2, "b", box)), "b")["id"] == "2"
    assert mesh_object(model((1, "whatever", box)), "b")["id"] == "1"
    with pytest.raises(Refused):
        mesh_object(model((1, "a", box), (2, "c", box)), "b")


def test_inlay_solids_by_name_or_the_loose_bodies():
    solids = {"Body1": 1, "Body12": 2, "counter-face-b-inlay": 3, "simple-counter-face": 4}
    assert step.inlay_solids(solids) == [1, 2]
    assert step.inlay_solids(solids, "counter-face-b-inlay") == [3]
    assert step.inlay_solids(solids, "missing-inlay") == []


def two_colour_template():
    """A two-colour counter-face file as the repo has them: face, inlay and the group."""
    box = trimesh.creation.box()
    xml = model((1, "simple-counter-face", box), (2, "counter-face-inlay", box))
    xml = xml.replace("<resources>", '<metadata name="Title">simple-counter-face-two-colour</metadata>\n <resources>')
    return xml.replace(" </resources>", '  <object id="3" type="model" name="simple-counter-face-two-colour">\n'
                                        '   <components>\n    <component objectid="1"/>\n'
                                        '    <component objectid="2"/>\n   </components>\n  </object>\n </resources>')


def test_two_colour_model_puts_a_part_and_its_inlay_in_the_counter_face_layout():
    knob = trimesh.creation.cylinder(radius=14, height=13.4)
    arrow = trimesh.creation.box((6, 2, 1))
    xml = two_colour_model(two_colour_template(), knob, arrow, "advance-knob", "advance-knob-inlay")
    meshes = {o["name"]: o["mesh"] for o in threemf.objects(xml) if o["mesh"] is not None}
    assert list(meshes) == ["advance-knob", "advance-knob-inlay"]
    assert abs(meshes["advance-knob"].volume - knob.volume) < 1e-3
    assert abs(meshes["advance-knob-inlay"].volume - arrow.volume) < 1e-3
    assert '<metadata name="Title">advance-knob-two-colour</metadata>' in xml
    assert 'name="advance-knob-two-colour"' in xml and '<component objectid="2"/>' in xml
    assert "counter-face" not in xml


def test_two_colour_model_refuses_a_template_without_one_inlay():
    box = trimesh.creation.box()
    with pytest.raises(Refused):
        two_colour_model(model((1, "simple-counter-face", box)), box, box, "advance-knob", "advance-knob-inlay")
