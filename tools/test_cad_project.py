import json
import zipfile

import numpy as np
import pytest
import trimesh

from cad import project, threemf
from cad.project import GAP, NoRoom, Project, columns, free_spot, plate_origin
from shapely.geometry import box

BED = 256.0
STRIDE = BED * 1.2


def object_file(mesh_id, mesh):
    vs, ts = threemf.mesh_lines(mesh, "     ")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" '
            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06">\n <resources>\n'
            f'  <object id="{mesh_id}" p:UUID="0000000{mesh_id}-81cb" type="model">\n   <mesh>\n    <vertices>{vs}\n'
            f'    </vertices>\n    <triangles>{ts}\n    </triangles>\n   </mesh>\n  </object>\n </resources>\n <build/>\n</model>\n')


def settings_object(oid, name, faces):
    return (f'  <object id="{oid}">\n    <metadata key="name" value="{name}"/>\n'
            f'    <metadata key="wall_loops" value="8"/>\n    <metadata face_count="{faces}"/>\n'
            f'    <part id="{oid - 1}" subtype="normal_part" uuid="uuid-{oid}">\n'
            f'      <metadata key="name" value="{name}"/>\n'
            f'      <metadata key="source_file" value="big.3mf"/>\n'
            f'      <metadata key="source_object_id" value="7"/>\n'
            f'      <metadata key="source_offset_x" value="12.5"/>\n'
            f'      <mesh_stat face_count="{faces}" edges_fixed="0"/>\n    </part>\n  </object>\n')


def make_project(path, plates, cols=None):
    """A small Bambu-style project. `plates` is a list of plates, each a list of
    (name, (sx, sy, sz) box size, (x, y) centre on the plate's bed)."""
    cols = cols or columns(len(plates))
    resources, items, rels, objs, plate_xml, assemble, cut = [], [], [], [], [], [], []
    files = {}
    oid = 0
    for p, content in enumerate(plates, 1):
        x0, y0 = plate_origin(p, cols, BED, BED)
        inst = []
        for name, size, (x, y) in content:
            oid += 2
            mesh = trimesh.creation.box(size)
            files[f"3D/Objects/object_{oid // 2}.model"] = object_file(oid - 1, mesh)
            resources.append(f'  <object id="{oid}" p:UUID="0000{oid:04x}-61cb" type="model">\n   <components>\n'
                             f'    <component p:path="/3D/Objects/object_{oid // 2}.model" objectid="{oid - 1}" '
                             f'p:UUID="{oid:04x}0000-b206" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>\n  </object>\n')
            items.append(f'  <item objectid="{oid}" p:UUID="{oid:08x}-b1ec" '
                         f'transform="1 0 0 0 1 0 0 0 1 {x0 + x} {y0 + y} {size[2] / 2}" printable="1"/>\n')
            rels.append(f' <Relationship Target="/3D/Objects/object_{oid // 2}.model" Id="rel-{oid // 2}" Type="t"/>\n')
            objs.append(settings_object(oid, name, len(mesh.faces)))
            inst.append(project.instance_block(oid, 1000 + oid))
            assemble.append(f'   <assemble_item object_id="{oid}" instance_id="0" transform="1 0 0 0 1 0 0 0 1 0 0 0" offset="0 0 0" />\n')
            cut.append(f' <object id="{oid // 2}">\n  <cut_id id="0" check_sum="1" connectors_cnt="0"/>\n </object>\n')
        plate_xml.append(f'  <plate>\n    <metadata key="plater_id" value="{p}"/>\n'
                         f'    <metadata key="plater_name" value="Plate {p}"/>\n    <metadata key="locked" value="false"/>\n'
                         f'    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
                         f'    <metadata key="thumbnail_file" value="Metadata/plate_{p}.png"/>\n' + "".join(inst) + "  </plate>\n")
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" '
             'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06">\n <resources>\n'
             + "".join(resources) + ' </resources>\n <build p:UUID="b">\n' + "".join(items) + " </build>\n</model>\n")
    settings = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "".join(objs) + "".join(plate_xml)
                + "  <assemble>\n" + "".join(assemble) + "  </assemble>\n</config>\n")
    printer = {"printable_area": ["0x0", "256x0", "256x256", "0x256"], "bed_exclude_area": ["0x0", "18x0", "18x28", "0x28"]}
    seq = {f"plate_{p}": {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []} for p in range(1, len(plates) + 1)}
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("3D/3dmodel.model", model)
        z.writestr("3D/_rels/3dmodel.model.rels", "<Relationships>\n" + "".join(rels) + "</Relationships>\n")
        for name, text in files.items():
            z.writestr(name, text)
        z.writestr("Metadata/project_settings.config", json.dumps(printer))
        z.writestr("Metadata/model_settings.config", settings)
        z.writestr("Metadata/cut_information.xml", "<objects>\n" + "".join(cut) + "</objects>\n")
        z.writestr("Metadata/filament_sequence.json", json.dumps(seq, separators=(",", ":")))
    return path


def on_plate(proj, name):
    """(plate, x, y of the object's centre relative to its plate's bed corner)."""
    o = proj.object_named(name)
    plate = proj.plate_of(o["object_id"])
    x0, y0 = proj.origin(plate)
    c = proj.placed(o["object_id"]).centroid
    return plate, round(c.x - x0, 6), round(c.y - y0, 6)


def test_columns_follow_bambu_studio():
    # compute_colum_count: sqrt rounded, plus one when the root is above its rounding
    assert [columns(n) for n in range(1, 18)] == [1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 5]


def test_plate_origin_uses_the_bed_plus_a_fifth():
    assert plate_origin(1, 3, BED, BED) == (0, 0)
    assert plate_origin(5, 3, BED, BED) == pytest.approx((STRIDE, -STRIDE))
    assert plate_origin(5, 4, BED, BED) == pytest.approx((0, -STRIDE))


def test_adding_a_plate_that_changes_the_columns_moves_every_object_with_its_plate(tmp_path):
    path = make_project(tmp_path / "p.3mf", [[(f"part-{p}", (20, 10, 4), (100 + p, 80))] for p in range(1, 10)])
    proj = Project(path)
    assert proj.cols() == 3
    before = {f"part-{p}": on_plate(proj, f"part-{p}") for p in range(1, 10)}

    assert proj.add_plate('Counter "cover" & more') == 10
    assert proj.cols() == 4
    proj.save()

    proj = Project(path)
    assert {n: on_plate(proj, n) for n in before} == before
    # plate 5 moved from column 2 of row 2 to column 1 of row 2
    t = proj.translation(proj.object_named("part-5")["object_id"])
    np.testing.assert_allclose(t[:2], [105, -STRIDE + 80], atol=1e-6)
    new = proj.plates()[-1]
    assert (new["id"], new["name"], new["objects"]) == (10, 'Counter "cover" & more', [])
    settings = proj.read(project.SETTINGS)
    block = settings[settings.index('value="10"'):]
    assert "&quot;cover&quot; &amp; more" in block and "thumbnail" not in block.split("</plate>")[0]
    assert "plate_10" in json.loads(proj.read(project.SEQUENCE))
    assert proj.plate_problems() == []


def test_adding_a_plate_within_the_same_columns_moves_nothing(tmp_path):
    path = make_project(tmp_path / "p.3mf", [[("a", (20, 10, 4), (100, 80))] for _ in range(5)])
    proj = Project(path)
    model = proj.read(project.MODEL)
    proj.add_plate("six")
    assert proj.read(project.MODEL) == model


def test_move_puts_an_object_on_a_free_spot_clear_of_the_others(tmp_path):
    path = make_project(tmp_path / "p.3mf", [[("big", (200, 200, 5), (128, 128)), ("small", (15, 15, 3), (245, 15))],
                                            [("gear", (20, 20, 4), (128, 128))]])
    proj = Project(path)
    gear = proj.object_named("gear")["object_id"]
    # plate 1 has room only in the 28 mm band round the big part, and not in the excluded corner
    assert proj.move(gear, "Plate 1") == 1
    proj.save()

    proj = Project(path)
    assert proj.plate_of(gear) == 1 and proj.plates()[1]["objects"] == []
    assert proj.plate_problems() == []
    assert proj.placed(gear).distance(proj.placed(proj.object_named("big")["object_id"])) >= GAP
    assert proj.shape(gear)[1] == pytest.approx(0)


def test_move_refuses_when_there_is_no_room(tmp_path):
    path = make_project(tmp_path / "p.3mf", [[("big", (240, 240, 5), (128, 128))], [("gear", (20, 20, 4), (128, 128))]])
    proj = Project(path)
    with pytest.raises(NoRoom):
        proj.move(proj.object_named("gear")["object_id"], 1)


def test_free_spot_prefers_the_point_asked_for():
    bed = box(0, 0, 100, 100)
    shape = box(-5, -5, 5, 5)
    dx, dy = free_spot(shape, bed, [box(30, 30, 70, 70)], near=(50, 50))
    placed = box(dx - 5, dy - 5, dx + 5, dy + 5)
    assert not placed.intersects(box(30, 30, 70, 70))
    # just outside the blocked square (touching counts as blocked), on an axis
    assert min(abs(dx - 50), abs(dy - 50)) == 0 and 25 < abs(dx - 50) + abs(dy - 50) <= 26


def test_plate_problems_finds_parts_too_close_off_the_bed_or_in_the_corner(tmp_path):
    path = make_project(tmp_path / "p.3mf", [[("a", (20, 20, 4), (100, 100)), ("b", (20, 20, 4), (123, 100)),
                                             ("c", (20, 20, 4), (250, 100)), ("d", (10, 10, 4), (8, 8))]])
    problems = Project(path).plate_problems()
    assert (1, "a / b", "only 3.00 mm apart") in problems
    assert (1, "c", "off the bed") in problems
    assert (1, "d", "in the bed's excluded area") in problems


def test_rename_plate(tmp_path):
    proj = Project(make_project(tmp_path / "p.3mf", [[("a", (20, 20, 4), (100, 100))], []]))
    proj.rename_plate(2, "Counter face - simple 25 (0.2 mm nozzle if possible)")
    assert proj.plate("Counter face - simple 25 (0.2 mm nozzle if possible)") == 2
    assert proj.plates()[0]["name"] == "Plate 1"


def test_clone_settings_object_copies_print_settings_under_a_new_name():
    settings = ('<config>\n' + settings_object(34, "simple-counter-face", 12) + settings_object(36, "other", 8)
                + '  <assemble>\n   <assemble_item object_id="34" instance_id="0" transform="1 0 0 0 1 0 0 0 1 5 6 7" offset="0 0 0" />\n'
                '  </assemble>\n</config>\n')
    out = project.clone_settings_object(settings, "34", 70, "simple-counter-face-20", 480, "simple-counter-face-20.3mf", "u-70")
    block = project.settings_object_block(out, 70)
    assert out.index('<object id="34">') < out.index('<object id="70">') < out.index('<object id="36">')
    assert block.count('value="simple-counter-face-20"') == 2
    assert '<part id="69"' in block and 'uuid="u-70"' in block
    assert block.count('face_count="480"') == 2
    assert 'key="wall_loops" value="8"' in block
    assert 'key="source_file" value="simple-counter-face-20.3mf"' in block
    assert 'key="source_object_id" value="0"' in block and 'key="source_offset_x" value="0"' in block
    assert '<assemble_item object_id="70" instance_id="0" transform="1 0 0 0 1 0 0 0 1 5 6 7"' in out
    assert project.settings_object_block(out, 34) == project.settings_object_block(settings, 34)


def test_clone_object_adds_a_complete_object_that_reads_back(tmp_path):
    path = make_project(tmp_path / "p.3mf", [[("face", (20, 20, 4), (60, 60))]])
    proj = Project(path)
    sibling = proj.object_named("face")
    mesh = trimesh.creation.cylinder(radius=10, height=4, sections=48)
    oid = proj.clone_object(sibling, "face-20", mesh, "face-20.3mf")
    proj.move(oid, 1)
    proj.save()

    proj = Project(path)
    new = proj.object_named("face-20")
    assert new["object_id"] == oid and new["mesh_file"] == "3D/Objects/object_2.model"
    assert len(proj.local_mesh(new).faces) == len(mesh.faces)
    assert proj.plate_of(oid) == 1 and proj.plate_problems() == []
    assert "/3D/Objects/object_2.model" in proj.read(project.RELS)
    assert proj.read(project.CUT).count("<object id=") == 2
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
    assert names.index("3D/Objects/object_2.model") < names.index("Metadata/model_settings.config")
    with pytest.raises(ValueError):
        proj.clone_object(new, "face-20", mesh, "face-20.3mf")
