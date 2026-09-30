"""Figure 4 of the hardware guide: the top cover round the take-up bore, with plungers P4-P6.

Drawn from the STEP, so rerun it after any change to the cover's take-up bore or its plunger
holes: mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import box

import common
from common import DOCS, INK, MUTED, badge, cylinders, draw, save
from cad import step  # noqa: E402

OUT = DOCS / 'fig2_cover_plungers.png'
DPI = 160   # the README's figures keep the size and type scale of the originals they replace
COVER = step.load_solids(names={'simple-cover'})['simple-cover']   # drag-cover has the same holes
MESH = step.tessellate(COVER, 0.01, 0.1)

# the plunger holes are the cover's only horizontal Ø2.2 holes; the cut goes along their axes
holes = [(a + b) / 2 for a, b in cylinders(COVER, 1.1) if abs(a[2] - b[2]) < 0.01]
if len(holes) != 3:
    raise SystemExit(f'expected three plunger holes round the take-up bore, found {len(holes)}')
Z = np.mean([h[2] for h in holes])
CX, CY = np.mean(holes, axis=0)[:2]   # three holes 120 degrees apart: their centre is the bore axis

# P4 points from the back, P5 from the front on the take-up end side, P6 from the front on the gear-bay side
back = max(holes, key=lambda h: h[0])
front = sorted((h for h in holes if h is not back), key=lambda h: -h[1])
# (hole, name, badge offset in Y, badge offset in X)
PLUNGERS = [(back, 'P4', 0, 7), (front[0], 'P5', 6, -4), (front[1], 'P6', -6, -4)]

cx, cy = round(CX), round(CY)   # frame the view on the bore, to the nearest mm
fig = plt.figure(figsize=(915 / DPI, 990 / DPI))
fig.subplots_adjust(left=0.0897, right=0.9834, bottom=0.0783, top=0.9501)
ax = fig.add_subplot()
# the cover is cut off 16 mm behind the bore, leaving room over it for P4's badge
cut = common.section(MESH, [0, 0, Z], [0, 0, 1], [1, 0])
draw(ax, cut.intersection(box(cy - 30, cx - 30, cy + 30, cx + 16)), '#e3e3e3')
for h, name, dy, dx in PLUNGERS:
    badge(ax, h[1], h[0], name, h[1] + dy, h[0] + dx, size=11)
ax.text(cy, cx - 17.15, 'FRONT (lens side)', ha='center', va='center', fontsize=9, color=MUTED)

ax.set_xlim(cy + 17, cy - 19); ax.set_ylim(cx - 19, cx + 19); ax.set_aspect('equal')
ax.set_xlabel('Y (mm)', fontsize=10, labelpad=1.75); ax.set_ylabel('X (mm)', fontsize=10)
ax.tick_params(length=3, labelsize=8)
ax.tick_params(axis='x', pad=1.7)
ax.set_title(f'Top cover round the take-up bore (cut at z = {Z:.1f} mm)', loc='left', fontsize=12,
             fontweight='bold', color=INK)
save(fig, OUT, DPI)
