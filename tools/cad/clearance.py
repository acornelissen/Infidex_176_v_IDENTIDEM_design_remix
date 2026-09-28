"""Check the counter gears against the body, the covers and each other, as assembled in the STEP.

The counter-train Fusion script checks the gears against each other and the round parts
in the bay, but cannot see the body walls or the covers. This reports, for every pair of
parts that are in the camera together, the volume they share and the smallest gap.

Some parts are alternatives, of which a camera has one: the simple or the drag cover, the
25-frame or the 20-frame idler set, and one counter face. Alternatives are never checked
against each other. Each idler set is checked with the shared gears (its train runs
ratchet-coupling-gear, counter-coupling-gear, idler 1 of the set, idler 2 of the set,
counter-gear) and against the housings; each face against every cover and against
counter-gear, which holds it. Options missing from the STEP are skipped with a note.

Meshing pairs (a pinion driving the next wheel in its train, as in gearcalc) run with
their teeth interleaved, so they are reported but not judged; their tooth clearance is
the gear maths' job. Any other pair that shares more than OVERLAP_LIMIT mm3 fails.

Usage: python -m cad.clearance [--step FILE]
Exits 1 on any overlap between parts that should not touch, or a fixed part missing.
"""
import argparse
import sys

from OCP.Bnd import Bnd_Box
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer

from . import STEP, user_path
from . import step

# in every camera; ratchet-coupling-gear carries the sprocket pinion (axis 0)
SPROCKET_END = ["ratchet-coupling-gear", "counter-coupling-gear"]
DIAL = "counter-gear"
BODY = ["body-solid", "body-top"]   # the one-piece body and its top half, each checked on its own
# alternatives: a camera has one of each
COVERS = ["simple-cover", "drag-cover"]
IDLER_SETS = {"25 frames": ["counter-idler-1", "counter-idler-2"],
              "20 frames": ["counter-idler-1-20", "counter-idler-2-20"]}
FACES = ["simple-counter-face", "drag-counter-face", "simple-counter-face-20", "drag-counter-face-20"]
FIXED = SPROCKET_END + [DIAL] + BODY
OVERLAP_LIMIT = 1e-3   # mm3
REACH = 1.0            # mm; gaps larger than this are only reported as "> REACH"


def near_part(shape, around):
    """The piece of `shape` inside the bounding box of `around` grown by REACH. Overlap and
    any gap under REACH are the same as for the whole shape, and far quicker to find."""
    box = Bnd_Box()
    BRepBndLib.Add_s(around, box, False)
    box.Enlarge(REACH)
    return BRepAlgoAPI_Common(shape, BRepPrimAPI_MakeBox(box.CornerMin(), box.CornerMax()).Shape()).Shape()


def is_empty(shape):
    return not TopExp_Explorer(shape, TopAbs_FACE).More()


def check(a, b):
    """(shared volume mm3, smallest gap mm or None if over REACH) between solids a and b."""
    piece = near_part(b, a)
    if is_empty(piece):
        return 0.0, None
    shared = step.volume(BRepAlgoAPI_Common(a, piece).Shape())
    return shared, BRepExtrema_DistShapeShape(a, piece).Value()


def train(idlers):
    """The gears of one build, sprocket end to dial end."""
    return SPROCKET_END + list(idlers) + [DIAL]


def pairs(present):
    """[(part, other part, meshing)] for every pair to check, given the set of part names in
    the STEP, and [notes] on options left out. Each pair appears once."""
    notes, out, seen = [], [], set()

    def add(a, b, meshing=False):
        if frozenset((a, b)) not in seen:
            seen.add(frozenset((a, b)))
            out.append((a, b, meshing))

    covers = [c for c in COVERS if c in present]
    housing = BODY + covers
    for label, idlers in IDLER_SETS.items():
        missing = [i for i in idlers if i not in present]
        if missing:
            notes.append(f"idler set {label} skipped: not in the STEP: {', '.join(missing)}")
            continue
        gears = train(idlers)
        meshing = {frozenset(p) for p in zip(gears, gears[1:])}
        for i, a in enumerate(gears):
            for b in gears[i + 1:]:
                add(a, b, frozenset((a, b)) in meshing)
        for g in gears:
            for h in housing:
                add(g, h)
    for face in FACES:
        if face not in present:
            notes.append(f"face {face} skipped: not in the STEP")
            continue
        for other in covers + [DIAL]:
            add(face, other)
    notes += [f"cover {c} skipped: not in the STEP" for c in COVERS if c not in present]
    return out, notes


def main(argv=None):
    ap = argparse.ArgumentParser(prog="clearance", description=__doc__.splitlines()[0])
    ap.add_argument("--step", type=user_path, default=STEP, help="STEP file to check (default: the one in cad/)")
    args = ap.parse_args(argv)

    wanted = set(FIXED + COVERS + FACES + [i for s in IDLER_SETS.values() for i in s])
    solids = step.load_solids(args.step, wanted)
    missing = sorted(set(FIXED) - set(solids))
    if missing:
        print(f"not in the STEP: {', '.join(missing)}")
        return 1
    todo, notes = pairs(set(solids))
    failed = 0
    print(f"{'part':24s} {'against':24s} {'kind':6s} {'overlap mm3':>11s} {'min gap mm':>10s}  result")
    for a, b, meshing in todo:
        shared, gap = check(solids[a], solids[b])
        bad = shared > OVERLAP_LIMIT and not meshing
        failed += bad
        verdict = "meshes, not judged" if meshing else ("FAIL overlap" if bad else "ok")
        gap_text = f"{gap:.3f}" if gap is not None else f"> {REACH:.1f}"
        print(f"{a:24s} {b:24s} {'mesh' if meshing else 'clear':6s} {shared:11.4f} {gap_text:>10s}  {verdict}")
    for note in notes:
        print(f"note: {note}")
    print(f"\n{len(todo)} pairs checked, {failed} overlapping that should not")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
