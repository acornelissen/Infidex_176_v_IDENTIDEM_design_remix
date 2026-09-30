"""Figure 3 of the hardware guide: the body's rewind bore from above, with plungers P1-P3.

Drawn from the STEP, so rerun it after any change to the body's rewind bore or its plunger
holes: mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt

import common
from common import DOCS, INK, badge, cylinders, draw, save
from cad import step  # noqa: E402

OUT = DOCS / 'fig3_rewind_plungers.png'
DPI = 160   # the README's figures keep the size and type scale of the originals they replace
BODY = step.load_solids(names={'body-solid'})['body-solid']
MESH = step.tessellate(BODY, 0.01, 0.1)

# the plunger holes are the Ø2.2 radial holes at the rewind end; the cut goes along their axes
holes = [(a + b) / 2 for a, b in cylinders(BODY, 1.1) if abs(a[2] - b[2]) < 0.01 and a[1] < -120]
if len(holes) != 3:
    raise SystemExit(f'expected three plunger holes round the rewind bore, found {len(holes)}')
Z = np.mean([h[2] for h in holes])
CX, CY = np.mean(holes, axis=0)[:2]   # three holes 120 degrees apart: their centre is the bore axis

# P1 points from the back, P2 from the front on the take-up side, P3 from the front on the rewind side
back = max(holes, key=lambda h: h[0])
front = sorted((h for h in holes if h is not back), key=lambda h: -h[1])
# (hole, name, badge offset in Y, badge offset in X)
PLUNGERS = [(back, 'P1', 0, 5), (front[0], 'P2', 5, -4), (front[1], 'P3', -5, -4)]

fig = plt.figure(figsize=(881 / DPI, 916 / DPI))
fig.subplots_adjust(left=0.093, right=0.9495, bottom=0.0835, top=0.9448)
ax = fig.add_subplot()
draw(ax, common.section(MESH, [0, 0, Z], [0, 0, 1], [1, 0]), '#e3e3e3')
for h, name, dy, dx in PLUNGERS:
    badge(ax, h[1], h[0], name, h[1] + dy, h[0] + dx, size=11)

cx, cy = round(CX), round(CY)   # frame the view on the bore, to the nearest mm
ax.set_xlim(cy + 11, cy - 11); ax.set_ylim(cx - 10, cx + 13); ax.set_aspect('equal')
ax.set_xlabel('Y (mm)', fontsize=10, labelpad=1.75); ax.set_ylabel('X (mm)', fontsize=10)
ax.tick_params(length=3, labelsize=8)
ax.tick_params(axis='x', pad=1.7)
ax.set_title(f'Rewind shaft bore, from above (z = {Z:.1f} mm)', loc='left', fontsize=12, fontweight='bold',
             color=INK)
save(fig, OUT, DPI)
