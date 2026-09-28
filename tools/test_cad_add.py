import pytest
import trimesh

from cad import step, threemf
from cad.add import Refused, mesh_object, rename
from test_cad_threemf import model


def test_rename_swaps_whole_names_and_the_title():
    xml = model((1, "simple-counter-face", trimesh.creation.box()), (2, "counter-face-inlay", trimesh.creation.box()))
    xml = xml.replace("<resources>", '<metadata name="Title">simple-counter-face-two-colour</metadata>\n <resources>')
    xml += '<object id="3" name="simple-counter-face-two-colour"/>'
    out = rename(xml, {"simple-counter-face": "simple-counter-face-20", "counter-face-inlay": "counter-face-20-inlay",
                       "simple-counter-face-two-colour": "simple-counter-face-20-two-colour"})
    assert [o["name"] for o in threemf.objects(out)] == ["simple-counter-face-20", "counter-face-20-inlay"]
    assert '<metadata name="Title">simple-counter-face-20-two-colour</metadata>' in out
    assert 'name="simple-counter-face-20-two-colour"' in out


def test_mesh_object_takes_the_named_mesh_or_the_only_one():
    box = trimesh.creation.box()
    assert mesh_object(model((1, "a", box), (2, "b", box)), "b")["id"] == "2"
    assert mesh_object(model((1, "whatever", box)), "b")["id"] == "1"
    with pytest.raises(Refused):
        mesh_object(model((1, "a", box), (2, "c", box)), "b")


def test_inlay_solids_by_name_or_the_loose_bodies():
    solids = {"Body1": 1, "Body12": 2, "counter-face-20-inlay": 3, "simple-counter-face": 4}
    assert step.inlay_solids(solids) == [1, 2]
    assert step.inlay_solids(solids, "counter-face-20-inlay") == [3]
    assert step.inlay_solids(solids, "missing-inlay") == []
