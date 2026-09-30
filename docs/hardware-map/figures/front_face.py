"""Figure 2 of the hardware guide: the body's front face with the lens standard removed, and the
four lens standard inserts I8-I11.

Drawn from the STEP, so rerun it after any change to the body's front face: mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from shapely.geometry import Polygon

import common
from common import IMG, INK, MUTED, draw, save
from cad import step  # noqa: E402

OUT = IMG / 'front-face.png'
BODY = 'body-solid'
M = step.tessellate(step.load_solids(names={BODY})[BODY], 0.01, 0.1)
CUT = 2.0              # the cut is this far behind the face, inside the 4 mm insert holes
INSERT_HOLE = (3.5, 5.0)   # the insert holes are the round holes of a diameter in this range
BADGE = '#0072b2'
plt.rcParams['font.size'] = 8
# badge offsets from each insert, in mm: up and outwards for the top pair, down for the bottom
OFFSET = {'I8': (-8.8, 8.2), 'I9': (8.8, 8.2), 'I10': (-8.8, -8.0), 'I11': (8.8, -8.0)}

# the front face is where a ray from the lens side first meets the body, at the middle of its height
(_, y0, z0), (_, y1, z1) = M.bounds
loc, _, _ = M.ray.intersects_location([[0, (y0 + y1) / 2, 30.0]], [[1, 0, 0]])
face = loc[:, 0].min()
cut = common.section(M, [face + CUT, 0, 0], [1, 0, 0], [1, 2])

holes = []
for g in getattr(cut, 'geoms', [cut]):
    for h in g.interiors:
        ring = Polygon(h)
        d = 2 * np.sqrt(ring.area / np.pi)
        if INSERT_HOLE[0] < d < INSERT_HOLE[1] and ring.length < 1.1 * np.pi * d:
            holes.append(ring.centroid.coords[0])
# name them as the guide does: I8 upper take-up side, I9 upper rewind, I10 and I11 below
holes.sort(key=lambda p: (-round(p[1]), -p[0]))
names = dict(zip(['I8', 'I9', 'I10', 'I11'], holes))

fig, ax = plt.subplots(figsize=(7.925, 3.715))
draw(ax, cut, '#e3e3e3')
for name, (y, z) in names.items():
    dy, dz = OFFSET[name]
    ax.annotate('', (y, z), (y + dy, z + dz), arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=8)
    ax.plot(y, z, 'o', ms=4.5, mfc=BADGE, mec=INK, mew=0.8, zorder=9)
    ax.text(y + dy, z + dz, name, ha='center', va='center', fontsize=9, fontweight='bold', color='white', zorder=10,
            bbox=dict(boxstyle='circle,pad=0.3', fc=BADGE, ec=INK, lw=0.9))
ax.text(-25, 47, 'take-up end', ha='center', va='center', fontsize=8.5, color=MUTED, zorder=6)
ax.text(-148, 47, 'rewind end', ha='center', va='center', fontsize=8.5, color=MUTED, zorder=6)

ax.set_xlim(4.3, -175.5); ax.set_ylim(-25.3, 50); ax.set_aspect('equal')
ax.set_xlabel('Y (mm)', fontsize=9); ax.set_ylabel('Z (mm)', fontsize=9)
ax.tick_params(length=3)
ax.xaxis.set_major_locator(MultipleLocator(25))
ax.set_title(f'Body front face, seen from the front (lens standard removed; cut {CUT:g} mm behind the face)',
             loc='left', fontsize=9.5, fontweight='bold', color=INK)
fig.tight_layout()
save(fig, OUT)
