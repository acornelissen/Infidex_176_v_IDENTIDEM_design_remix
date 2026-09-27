"""Check the counter gears against the body, the covers and each other, as assembled in the STEP.

The counter-train Fusion script checks the gears against each other and the round parts
in the bay, but cannot see the body walls or the covers. This reports, for every gear
against every housing part and every other gear, the volume they share and the smallest
gap between them.

Meshing pairs (a pinion driving the next wheel in the train, as in gearcalc) run with
their teeth interleaved, so they are reported but not judged; their tooth clearance is
the gear maths' job. Any other pair that shares more than OVERLAP_LIMIT mm3 fails.

Usage: python -m cad.clearance [--step FILE]
Exits 1 on any overlap between parts that should not touch.
"""
import argparse
import itertools
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

# sprocket end to dial end; ratchet-coupling-gear carries the sprocket pinion (axis 0)
GEARS = ["ratchet-coupling-gear", "counter-coupling-gear", "counter-idler-1", "counter-idler-2", "counter-gear"]
# the one-piece body and its top half, and both covers; each is checked on its own
HOUSING = ["body-solid", "body-top", "simple-cover", "drag-cover"]
# the pinion on axis n drives the wheel on axis n + 1
MESHING = {frozenset(pair) for pair in zip(GEARS, GEARS[1:])}
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


def main(argv=None):
    ap = argparse.ArgumentParser(prog="clearance", description=__doc__.splitlines()[0])
    ap.add_argument("--step", type=user_path, default=STEP, help="STEP file to check (default: the one in cad/)")
    args = ap.parse_args(argv)

    solids = step.load_solids(args.step, set(GEARS + HOUSING))
    missing = sorted(set(GEARS + HOUSING) - set(solids))
    if missing:
        print(f"not in the STEP: {', '.join(missing)}")
        return 1
    pairs = list(itertools.combinations(GEARS, 2)) + [(g, h) for g in GEARS for h in HOUSING]
    failed = 0
    print(f"{'part':24s} {'against':24s} {'kind':6s} {'overlap mm3':>11s} {'min gap mm':>10s}  result")
    for a, b in pairs:
        shared, gap = check(solids[a], solids[b])
        meshing = frozenset((a, b)) in MESHING
        bad = shared > OVERLAP_LIMIT and not meshing
        failed += bad
        verdict = "meshes, not judged" if meshing else ("FAIL overlap" if bad else "ok")
        gap_text = f"{gap:.3f}" if gap is not None else f"> {REACH:.1f}"
        print(f"{a:24s} {b:24s} {'mesh' if meshing else 'clear':6s} {shared:11.4f} {gap_text:>10s}  {verdict}")
    print(f"\n{len(pairs)} pairs checked, {failed} overlapping that should not")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
