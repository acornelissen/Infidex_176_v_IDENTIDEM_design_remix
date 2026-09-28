from cad.clearance import BODY, COVERS, FACES, IDLER_SETS, pairs

TODAY = {"ratchet-coupling-gear", "counter-coupling-gear", "counter-gear", "counter-idler-1", "counter-idler-2",
         "body-solid", "body-top", "simple-cover", "drag-cover", "simple-counter-face", "drag-counter-face"}
WITH_20 = TODAY | set(IDLER_SETS["20 frames"]) | {"simple-counter-face-20", "drag-counter-face-20"}


def as_sets(todo):
    return {frozenset((a, b)): meshing for a, b, meshing in todo}


def test_alternatives_are_never_checked_against_each_other():
    got = as_sets(pairs(WITH_20)[0])
    groups = [COVERS, FACES, IDLER_SETS["25 frames"] + IDLER_SETS["20 frames"]]
    for group in groups[:2]:
        assert not any(frozenset((a, b)) in got for a in group for b in group if a != b)
    for a in IDLER_SETS["25 frames"]:
        for b in IDLER_SETS["20 frames"]:
            assert frozenset((a, b)) not in got
    assert len(got) == len(pairs(WITH_20)[0])   # each pair once


def test_each_idler_set_meshes_in_its_own_train():
    got = as_sets(pairs(WITH_20)[0])
    for i1, i2 in IDLER_SETS.values():
        assert got[frozenset(("counter-coupling-gear", i1))] is True
        assert got[frozenset((i1, i2))] is True
        assert got[frozenset((i2, "counter-gear"))] is True
        assert got[frozenset(("ratchet-coupling-gear", i2))] is False
        for h in BODY + COVERS:
            assert got[frozenset((i1, h))] is False
    assert got[frozenset(("ratchet-coupling-gear", "counter-coupling-gear"))] is True
    assert got[frozenset(("counter-coupling-gear", "counter-gear"))] is False


def test_faces_are_checked_against_every_cover_and_the_dial_gear():
    got = as_sets(pairs(WITH_20)[0])
    for face in FACES:
        for other in COVERS + ["counter-gear"]:
            assert got[frozenset((face, other))] is False
        assert frozenset((face, "body-solid")) not in got


def test_parts_not_in_the_step_are_skipped_with_a_note():
    todo, notes = pairs(TODAY)
    assert not any("-20" in a or "-20" in b for a, b, _ in todo)
    assert "idler set 20 frames skipped: not in the STEP: counter-idler-1-20, counter-idler-2-20" in notes
    assert "face simple-counter-face-20 skipped: not in the STEP" in notes
