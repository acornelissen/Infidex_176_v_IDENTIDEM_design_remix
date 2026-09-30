"""Figure 10 of the README and the hardware guide: the pressure plate in the door, from inside
and cut across at mid-height with the door open.

The STEP models the plate in its working position, pressed back onto the film rails, where its
end pads sit inside the door. With the door open the leaf is relaxed and the pads sit on the
floor of the door's recess, so both views move the plate out by that much.

Drawn from the STEP, so rerun it after any change to the pressure plate, the door or the film
rails in the body: mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
from shapely.affinity import translate
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import common
from common import DOCS, EDGE, INK, MUTED, draw, save
from cad import step  # noqa: E402

OUT = DOCS / 'fig10_pressure_plate.png'
PLATE, DOOR, BODY = 'pressure-plate (1)', 'door-var-3', 'body-solid'
BIG = {DOOR, BODY}   # slow to mesh at the fine tolerance
M = {n: step.tessellate(s, *((0.01, 0.1) if n in BIG else (0.003, 0.03)))
     for n, s in step.load_solids(names={PLATE, DOOR, BODY}).items()}
FILL = {PLATE: '#c8d3dc', DOOR: '#ebebeb', 'glue': '#cc79a7'}
# the bond pads are the ends of the leaf that lie within this of the door face
GLUE_GAP = 0.45
plt.rcParams['font.size'] = 8


def section(name, origin, normal, axes):
    return common.section(M[name], origin, normal, axes)


def hits(name, origin, direction):
    """Every point where a ray from `origin` crosses `name`, as distances along `direction`."""
    loc, _, _ = M[name].ray.intersects_location([origin], [direction])
    return sorted(np.dot(p - origin, direction) for p in loc)


def outline(name, step_mm=0.25):
    """Everything of `name` seen along X, from inside the door: its cuts at every step in X, joined."""
    (x0, _, _), (x1, _, _) = M[name].bounds
    cuts = [section(name, [x, 0, 0], [1, 0, 0], [1, 2]) for x in np.arange(x0 + 0.01, x1, step_mm)]
    return unary_union([c.buffer(0.01) for c in cuts])


(_, py0, pz0), (px1, py1, pz1) = M[PLATE].bounds
centre = np.array([(py0 + py1) / 2, (pz0 + pz1) / 2])
floor = 70 + hits(DOOR, [70, *centre], [1, 0, 0])[0]     # the floor of the door's recess
shift = floor - px1                                       # pads down onto the recess floor
rail = 60 + max(hits(BODY, [60, centre[0], pz0 + 1.5], [1, 0, 0]))   # the film rail faces
cut = section(DOOR, [floor - 0.1, 0, 0], [1, 0, 0], [1, 2])
recess = min((Polygon(h) for g in getattr(cut, 'geoms', [cut]) for h in g.interiors),
             key=lambda r: r.distance(Point(centre)))
plate = outline(PLATE)
pads = section(PLATE, [px1 - GLUE_GAP, 0, 0], [1, 0, 0], [1, 2])
pads = sorted(getattr(pads, 'geoms', [pads]), key=lambda g: -g.centroid.x)   # take-up end first

fig, (a1, a2) = plt.subplots(2, 1, figsize=(10.26, 6.345), gridspec_kw={'height_ratios': [1.95, 1]})

# ---- the door from inside, with the plate in its recess
door = outline(DOOR, 0.5)
draw(a1, door, FILL[DOOR])
draw(a1, plate, FILL[PLATE], z=2)
for p in pads:
    draw(a1, p, FILL['glue'], z=3)
    a1.text(p.centroid.x, pz1 + 2.5, 'bond pad', ha='center', va='center', fontsize=8.5, color=INK, zorder=6)
a1.plot(*recess.exterior.xy, color=INK, lw=0.9, ls='--', zorder=4)
a1.text(*centre, 'platen', ha='center', va='center', fontsize=9.5, color=INK, zorder=6)
a1.text(centre[0], pz1 + 2.3, '0.2 mm locating recess (dashed)', ha='center', va='center', color=MUTED, zorder=6)
(dy0, dz0, dy1, _) = door.bounds
a1.text(dy1 - 6, dz0 + 1, 'take-up end', ha='left', va='bottom', color=MUTED, zorder=6)
a1.text(dy0 + 6, dz0 + 1, 'rewind end', ha='right', va='bottom', color=MUTED, zorder=6)
a1.set_xlim(dy1 + 1.9, dy0 - 1); a1.set_aspect('equal')
a1.set_xlabel('Y (mm)', fontsize=9.5); a1.set_ylabel('Z (mm)', fontsize=9.5)
a1.tick_params(length=3)
a1.set_title('Door, inside face, with the pressure plate in its recess', loc='left', fontsize=10,
             fontweight='bold', color=INK)

# ---- cut across the door at mid-height, door open
z = centre[1]
draw(a2, section(DOOR, [0, 0, z], [0, 0, 1], [1, 0]), FILL[DOOR])
draw(a2, translate(section(PLATE, [0, 0, z], [0, 0, 1], [1, 0]), 0, shift), FILL[PLATE], z=2)
for p in pads:
    a2.annotate('bond pad on door face', (p.centroid.x, floor), (p.centroid.x, floor + 7.7), ha='center',
                va='center', fontsize=8, color=INK, arrowprops=dict(arrowstyle='->', color=INK, lw=0.9), zorder=10)
a2.axhline(rail, color=INK, lw=1.0, ls='--', zorder=5)
a2.text(centre[0] - 1.2, rail - 2.2, 'film plane (rail faces): closing the door pushes the platen back to here',
        ha='center', va='center', color=MUTED, zorder=6)
a2.set_xlim(-45, -140); a2.set_ylim(rail - 3.4, rail + 12.8); a2.set_aspect('equal')
a2.set_xlabel('Y (mm)', fontsize=9.5); a2.set_ylabel('X (mm)', fontsize=9.5)
a2.tick_params(length=3)
a2.yaxis.set_major_locator(MultipleLocator(2))
a2.set_title('Cut across the door at mid-height, door open: leaf bonded at both ends, platen free', loc='left',
             fontsize=10, fontweight='bold', color=INK)

fig.legend(handles=[Patch(fc=FILL[PLATE], ec=EDGE, label='pressure plate'),
                    Patch(fc=FILL['glue'], ec=EDGE, label='glue here'),
                    Patch(fc=FILL[DOOR], ec=EDGE, label='door')],
           loc='upper right', ncol=3, frameon=False, fontsize=8)
fig.tight_layout(h_pad=2.0)
save(fig, OUT)
