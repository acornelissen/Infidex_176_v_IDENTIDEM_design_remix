from cad.clearance import BODY, COVERS, FACES, IDLER_SETS, pairs

TODAY = {"ratchet-coupling-gear", "counter-coupling-gear", "counter-gear", "counter-idler-1", "counter-idler-2",
         "body-solid", "body-top", "simple-cover", "drag-cover", "simple-counter-face", "drag-counter-face"}
# a second idler set and face on the same axes, as a new option would be
SETS = {**IDLER_SETS, "b": ["idler-1-b", "idler-2-b"]}
ALL_FACES = FACES + ["face-b"]
WITH_B = TODAY | {"idler-1-b", "idler-2-b", "face-b"}


def as_sets(todo):
    return {frozenset((a, b)): meshing for a, b, meshing in todo}


def with_b():
    return as_sets(pairs(WITH_B, SETS, ALL_FACES)[0])


def test_alternatives_are_never_checked_against_each_other():
    got = with_b()
    for group in (COVERS, ALL_FACES):
        assert not any(frozenset((a, b)) in got for a in group for b in group if a != b)
    for a in IDLER_SETS["25 frames"]:
        for b in SETS["b"]:
            assert frozenset((a, b)) not in got
    assert len(got) == len(pairs(WITH_B, SETS, ALL_FACES)[0])   # each pair once


def test_each_idler_set_meshes_in_its_own_train():
    got = with_b()
    for i1, i2 in SETS.values():
        assert got[frozenset(("counter-coupling-gear", i1))] is True
        assert got[frozenset((i1, i2))] is True
        assert got[frozenset((i2, "counter-gear"))] is True
        assert got[frozenset(("ratchet-coupling-gear", i2))] is False
        for h in BODY + COVERS:
            assert got[frozenset((i1, h))] is False
    assert got[frozenset(("ratchet-coupling-gear", "counter-coupling-gear"))] is True
    assert got[frozenset(("counter-coupling-gear", "counter-gear"))] is False


def test_faces_are_checked_against_every_cover_and_the_dial_gear():
    got = with_b()
    for face in ALL_FACES:
        for other in COVERS + ["counter-gear"]:
            assert got[frozenset((face, other))] is False
        assert frozenset((face, "body-solid")) not in got


def test_the_default_options_are_todays_parts():
    todo, notes = pairs(TODAY)
    assert notes == []
    assert {p for pair in as_sets(todo) for p in pair} == TODAY


def test_options_not_in_the_step_are_skipped_with_a_note():
    todo, notes = pairs(TODAY, SETS, ALL_FACES)
    assert as_sets(todo) == as_sets(pairs(TODAY)[0])
    assert notes == ["idler set b skipped: not in the STEP: idler-1-b, idler-2-b", "face face-b skipped: not in the STEP"]
