from cad.verify import loose_solids


def test_loose_solids_leave_out_inlay_bodies_and_pieces_of_covered_inlays():
    solids = ["simple-counter-face", "Body3", "counter-face-20-inlay-1", "counter-face-20-inlay-2",
              "knob-inlay-1", "spare-part"]
    covered = {"simple-counter-face", "counter-face-20-inlay"}
    assert loose_solids(solids, covered) == ["knob-inlay-1", "spare-part"]
