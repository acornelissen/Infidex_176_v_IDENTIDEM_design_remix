"""Figure 5 of the hardware guide: one D2×3 ball plunger in its hole, cut through the plunger's axis.

The cut is P1's, at the back of the body's rewind bore. The plunger is bought, so it is drawn as
blocks from the README's sizes; the hole and the part around it come from the STEP.

Drawn from the STEP, so rerun it after any change to the plunger holes in the body or the covers:
mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from shapely.affinity import translate
from shapely.geometry import LineString, box

import common
from common import EDGE, IMG, INK, MUTED, PLUNGER, draw, on_axis, save
from cad import step  # noqa: E402

OUT = IMG / 'plunger-section.png'
S = step.load_solids(names={'body-solid', 'simple-cover'})
# P1 and P4 point in along -X, so a point on each axis and +X, out along the hole
OUTWARD = np.array([1.0, 0.0, 0.0])
P1 = np.array([72.0, -149.015, 40.579])   # body, back of the rewind bore
P4 = np.array([72.0, -25.016, 42.806])    # top cover, back of the take-up bore

# D2×3 flanged plunger: Ø2 body, Ø2.5 flange, 3 mm long overall, Ø1.5 ball 0.4 proud of the flange.
# The flange is taken as 0.5 thick, as in drag_option.py.
BODY_D, FLANGE_D, LENGTH, FLANGE_T, BALL_D, PROUD = 2.0, 2.5, 3.0, 0.5, 1.5, 0.4
PART = '#e3e3e3'


def seat_and_hole(name, point):
    """The flange seat and the hole behind it, as (diameter, start, end) out from `point`."""
    c = on_axis(S[name], point, OUTWARD)
    assert len(c) == 2 and c[0][0] > c[1][0], f'expected a seat and a hole on the plunger axis in {name}, found {c}'
    return c


(seat_d, seat_0, seat_1), (hole_d, hole_0, hole_1) = seat_and_hole('body-solid', P1)
_, (_, cover_0, cover_1) = seat_and_hole('simple-cover', P4)

# the body cut through P1's axis, shifted so x runs out along the hole from P1 and y up from its axis
cut = common.section(step.tessellate(S['body-solid'], 0.01, 0.1), P1, [0, 1, 0], [0, 2])
cut = translate(cut, -P1[0], -P1[2])
# the bore wall just beside the seat; the bore is upright, so the wall is straight in this cut
beside = seat_d / 2 + 0.05
wall = cut.intersection(LineString([(seat_0 - 2, -beside), (seat_1, -beside)])).bounds[0]

plt.rcParams['font.size'] = 7.2
fig = plt.figure(figsize=(3.905, 2.545))
ax = fig.add_axes([0, 0, 1, 1])
# the part, cut off square by a window but outlined only where it has a real face
win = box(wall - 1, -2.97, wall + 11.87, 2.97)
draw(ax, cut.intersection(win), PART, lw=0, ec='none')
for g in getattr(cut, 'geoms', [cut]):
    for ring in [g.exterior, *g.interiors]:
        edge = ring.intersection(win)
        for e in getattr(edge, 'geoms', [edge]):
            if not e.is_empty:
                ax.plot(*e.xy, color=EDGE, lw=0.8, zorder=2)

# plunger: flange on the seat floor, body in the hole, ball out of the flange face
flange_face = seat_1 - FLANGE_T
ax.add_patch(Rectangle((flange_face, -FLANGE_D / 2), FLANGE_T, FLANGE_D, fc=PLUNGER, ec=INK, lw=0.8, zorder=3))
ax.add_patch(Rectangle((seat_1, -BODY_D / 2), LENGTH - FLANGE_T, BODY_D, fc=PLUNGER, ec=INK, lw=0.8, zorder=3))
ax.add_patch(Circle((flange_face - PROUD + BALL_D / 2, 0), BALL_D / 2, fc='#bbbbbb', ec=INK, lw=0.8, zorder=4))

arrow = dict(arrowstyle='->', color=INK, lw=0.75)
ax.annotate('shaft bore\n(ball points in)', (wall - 0.5, 0.31), (wall - 2.98, 2.89), ha='left', va='center',
            color=INK, arrowprops=arrow)
ax.annotate(f'Ø{seat_d:.1f} × {seat_1 - seat_0:.2f} seat for the flange', (wall + 0.36, seat_d / 2 - 0.03),
            (wall + 4.39, 3.67), ha='center', va='center', color=INK, arrowprops=arrow)
ax.annotate(f'Ø{hole_d:.1f} × {hole_1 - hole_0:.1f} blind hole\n(× {cover_1 - cover_0:.1f} for P4–P6 in the cover)',
            (hole_1 - 0.1, -hole_d / 2), (wall + 6.88, -3.75), ha='center', va='center', color=INK, arrowprops=arrow)
ax.text(wall + 9.5, 0, 'printed part', ha='center', va='center', color=MUTED)

ax.set_xlim(wall - 3.52, wall - 3.52 + 781 / 49.7)   # 49.7 px/mm, as the figure was first drawn
ax.set_ylim(-4.8, 5.44)
ax.set_aspect('equal')
ax.axis('off')
fig.text(18 / 781, 1 - 29 / 509, 'D2×3 plunger in its hole (P1–P6)', ha='left', va='center', fontsize=9.4,
         fontweight='bold', color=INK)
save(fig, OUT)
