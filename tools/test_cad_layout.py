from cad.layout import apply
from cad.project import Project
from test_cad_project import make_project

LAYOUT = [("Cover A", ["cover-a"]), ("Idlers 25", ["idler-1", "idler-2"]), ("Idlers 20", ["idler-1-20", "idler-2-20"])]


def small_parts(tmp_path):
    return make_project(tmp_path / "p.3mf", [[("body", (150, 60, 30), (128, 128))] for _ in range(8)] + [
        [("cover-a", (40, 70, 6), (40, 120)), ("idler-1", (18, 18, 4), (120, 60)), ("idler-2", (18, 18, 4), (150, 60)),
         ("gear", (22, 22, 4), (180, 180))]])


def test_layout_gives_each_option_a_plate_and_leaves_shared_parts(tmp_path):
    proj = Project(small_parts(tmp_path))
    said = apply(proj, LAYOUT)
    assert "skipped 'Idlers 20': not in the project yet: idler-1-20, idler-2-20" in said
    names = {p["name"]: p for p in proj.plates()}
    assert set(names) == {f"Plate {n}" for n in range(1, 10)} | {"Cover A", "Idlers 25"}
    assert proj.cols() == 4   # 11 plates
    by_name = {o["object_id"]: o["name"] for o in proj.objects()}
    assert [by_name[o] for o in names["Cover A"]["objects"]] == ["cover-a"]
    assert sorted(by_name[o] for o in names["Idlers 25"]["objects"]) == ["idler-1", "idler-2"]
    assert [by_name[o] for o in names["Plate 9"]["objects"]] == ["gear"]
    assert proj.plate_problems() == []


def test_layout_runs_twice_without_changes(tmp_path):
    path = small_parts(tmp_path)
    proj = Project(path)
    apply(proj, LAYOUT)
    proj.save()
    proj = Project(path)
    model = proj.read("3D/3dmodel.model")
    said = apply(proj, LAYOUT)
    assert said == ["skipped 'Idlers 20': not in the project yet: idler-1-20, idler-2-20"]
    assert proj.read("3D/3dmodel.model") == model
