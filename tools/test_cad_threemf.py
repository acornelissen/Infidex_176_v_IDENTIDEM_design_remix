import zipfile

import numpy as np
import pytest
import trimesh

from cad import threemf


def model(*objects):
    """A part-file style model; objects are (id, name, mesh)."""
    parts = []
    for oid, name, mesh in objects:
        vs, ts = threemf.mesh_lines(mesh, "     ")
        parts.append(f'  <object id="{oid}" type="model" name="{name}">\n   <mesh>\n    <vertices>{vs}\n'
                     f'    </vertices>\n    <triangles>{ts}\n    </triangles>\n   </mesh>\n  </object>\n')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter">\n <resources>\n'
            + "".join(parts) + ' </resources>\n <build>\n  <item objectid="1"/>\n </build>\n</model>\n')


def test_mesh_round_trips_through_model_xml():
    box = trimesh.creation.box((10, 6, 3))
    [obj] = threemf.objects(model((1, "box", box)))
    assert obj["id"] == "1" and obj["name"] == "box"
    np.testing.assert_allclose(obj["mesh"].vertices, box.vertices, atol=1e-6)
    np.testing.assert_array_equal(obj["mesh"].faces, box.faces)
    assert obj["mesh"].is_watertight
    assert obj["mesh"].volume == pytest.approx(180, rel=1e-6)


def test_replace_mesh_changes_only_the_chosen_object():
    box, ball = trimesh.creation.box((1, 1, 1)), trimesh.creation.icosphere(1)
    xml = model((1, "face", box), (2, "inlay", box))
    new = threemf.replace_mesh(xml, ball, object_id=2)
    face, inlay = threemf.objects(new)
    np.testing.assert_allclose(inlay["mesh"].vertices, ball.vertices, atol=1e-6)
    np.testing.assert_array_equal(inlay["mesh"].faces, ball.faces)
    # the first object and everything around the second are untouched
    assert new.startswith(xml[:xml.index('<object id="2"')])
    assert new.endswith(xml[xml.index("  </object>\n </resources>"):])
    assert face["mesh"].vertices.shape == box.vertices.shape


def test_replace_mesh_needs_a_mesh_object():
    with pytest.raises(KeyError):
        threemf.replace_mesh(model((1, "box", trimesh.creation.box())), trimesh.creation.box(), object_id=7)


def test_rewrite_zip_keeps_every_other_entry_byte_for_byte(tmp_path):
    path = tmp_path / "part.3mf"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "types", compress_type=zipfile.ZIP_STORED)
        z.writestr("3D/3dmodel.model", "old model", compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("Metadata/plate_1.png", bytes(range(256)) * 10, compress_type=zipfile.ZIP_STORED)
    with zipfile.ZipFile(path) as z:
        before = {i.filename: (z.read(i.filename), i.compress_type) for i in z.infolist()}

    threemf.rewrite_zip(path, {"3D/3dmodel.model": "new model"})

    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        after = {i.filename: (z.read(i.filename), i.compress_type) for i in z.infolist()}
    assert list(after) == list(before)
    assert after["3D/3dmodel.model"] == (b"new model", zipfile.ZIP_DEFLATED)
    for name in ("[Content_Types].xml", "Metadata/plate_1.png"):
        assert after[name] == before[name]


def test_rewrite_zip_refuses_an_entry_it_does_not_have(tmp_path):
    path = tmp_path / "part.3mf"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("a", "1")
    with pytest.raises(KeyError):
        threemf.rewrite_zip(path, {"b": "2"})
    with zipfile.ZipFile(path) as z:
        assert z.namelist() == ["a"]


def test_transform_reads_3mf_row_vector_order():
    # 3MF multiplies row vectors: the first three numbers are where the x axis goes
    T = threemf.transform("0 1 0 -1 0 0 0 0 1 10 20 30")
    np.testing.assert_allclose(T @ [1, 0, 0, 1], [10, 21, 30, 1])
    np.testing.assert_allclose(threemf.transform(None), np.eye(4))


PROJECT_MODEL = """<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06">
 <resources>
  <object id="2" p:UUID="a" type="model">
   <components>
    <component p:path="/3D/Objects/object_7.model" objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 5"/>
   </components>
  </object>
  <object id="4" p:UUID="b" type="model">
   <components>
    <component p:path="/3D/Objects/object_9.model" objectid="3" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
   </components>
  </object>
 </resources>
 <build>
  <item objectid="2" transform="1 0 0 0 1 0 0 0 1 100 50 0" printable="1"/>
  <item objectid="4" transform="1 0 0 0 1 0 0 0 1 400 50 2" printable="1"/>
 </build>
</model>
"""

PROJECT_SETTINGS = """<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="2">
    <metadata key="name" value="counter-gear"/>
    <metadata face_count="12"/>
    <part id="1" subtype="normal_part">
      <mesh_stat face_count="12" edges_fixed="0"/>
    </part>
  </object>
  <object id="4">
    <metadata key="name" value="pressure-plate (1)"/>
    <metadata face_count="12"/>
  </object>
  <plate>
    <metadata key="plater_id" value="1"/>
    <model_instance>
      <metadata key="object_id" value="2"/>
    </model_instance>
  </plate>
  <plate>
    <metadata key="plater_id" value="2"/>
    <model_instance>
      <metadata key="object_id" value="4"/>
    </model_instance>
  </plate>
</config>
"""


def test_project_objects_lists_names_files_transforms_and_plates(tmp_path):
    path = tmp_path / "project.3mf"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("3D/3dmodel.model", PROJECT_MODEL)
        z.writestr("Metadata/model_settings.config", PROJECT_SETTINGS)
    gear, plate = threemf.project_objects(path)
    assert (gear["name"], gear["object_id"], gear["mesh_file"], gear["mesh_object_id"], gear["plate"]) == \
        ("counter-gear", "2", "3D/Objects/object_7.model", "1", 1)
    np.testing.assert_allclose(gear["transform"][:3, 3], [100, 50, 5])   # item after component
    assert (plate["name"], plate["plate"]) == ("pressure-plate (1)", 2)


def test_set_face_count_changes_only_that_object():
    out = threemf.set_face_count(PROJECT_SETTINGS, "2", 480)
    gear, rest = out.split('<object id="4">')
    assert gear.count('face_count="480"') == 2
    assert 'face_count="12"' not in gear
    assert rest == PROJECT_SETTINGS.split('<object id="4">')[1]
