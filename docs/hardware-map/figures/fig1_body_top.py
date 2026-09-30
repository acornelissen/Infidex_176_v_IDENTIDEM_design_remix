"""Figure 1 of the hardware guide: the body from above, with inserts I1-I7 and plungers P1-P3.

Drawn from the STEP, so rerun it after any change to the body's top face, its insert holes or
its plunger holes: mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt

import common
from common import DOCS, INK, INSERT, MUTED, badge, cylinders, draw, save
from cad import step  # noqa: E402

OUT = DOCS / 'fig1_body_top.png'
DPI = 160   # the README's figures keep the size and type scale of the originals they replace
BODY = step.load_solids(names={'body-solid'})['body-solid']
MESH = step.tessellate(BODY, 0.01, 0.1)

# Inserts in the top face: X and Y as in the guide's insert table, which the holes in the STEP
# must match to within SNAP mm, and where each badge sits relative to its hole (in Y, in X)
INSERTS = {
    'I1': (53.4, -9.1, 8, 10), 'I2': (76.4, -7.8, 8, 9), 'I3': (53.6, -40.1, 0, -11),
    'I4': (53.1, -74.7, 0, -11), 'I5': (80.2, -73.7, 0, 9), 'I6': (56.4, -98.8, -8, -11),
    'I7': (73.4, -99.2, 8, 10),
}
SNAP = 0.2
# M2 insert holes are Ø3.2 for the cover and Ø3.3 for the cold shoe
insert_holes = [(a + b) / 2 for r in (1.6, 1.65) for a, b in cylinders(BODY, r) if abs(a[0] - b[0]) < 0.01
                and abs(a[1] - b[1]) < 0.01]

# the plunger holes are the Ø2.2 radial holes at the rewind end; the cut goes along their axes
holes = [(a + b) / 2 for a, b in cylinders(BODY, 1.1) if abs(a[2] - b[2]) < 0.01 and a[1] < -120]
if len(holes) != 3:
    raise SystemExit(f'expected three plunger holes round the rewind bore, found {len(holes)}')
Z = np.mean([h[2] for h in holes])
# P1 points from the back, P2 from the front on the take-up side, P3 from the front on the rewind side
back = max(holes, key=lambda h: h[0])
front = sorted((h for h in holes if h is not back), key=lambda h: -h[1])
PLUNGERS = [(back, 'P1', 0, 11), (front[0], 'P2', 9, -9), (front[1], 'P3', -9, -9)]


def insert_badge(ax, x, y, text, tx, ty):
    ax.annotate('', (x, y), (tx, ty), arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=8)
    ax.plot(x, y, 'o', ms=4.5, mfc=INSERT, mec=INK, mew=0.8, zorder=9)
    ax.text(tx, ty, text, ha='center', va='center', fontsize=11, fontweight='bold', color='white', zorder=10,
            bbox=dict(boxstyle='circle,pad=0.22', fc=INSERT, ec=INK, lw=0.9))


fig = plt.figure(figsize=(1710 / DPI, 745 / DPI))
fig.subplots_adjust(left=0.0495, right=0.9902, bottom=0.1027, top=0.9320)
ax = fig.add_subplot()
draw(ax, common.section(MESH, [0, 0, Z], [0, 0, 1], [1, 0]), '#e3e3e3')

for name, (x, y, dy, dx) in INSERTS.items():
    near = min(insert_holes, key=lambda h: np.hypot(h[0] - x, h[1] - y))
    if np.hypot(near[0] - x, near[1] - y) > SNAP:
        raise SystemExit(f'{name}: no insert hole within {SNAP} mm of X {x}, Y {y} in the STEP')
    insert_badge(ax, near[1], near[0], name, near[1] + dy, near[0] + dx)
for h, name, dy, dx in PLUNGERS:
    badge(ax, h[1], h[0], name, h[1] + dy, h[0] + dx, size=11)

for y, x, text in [(-88, 93, 'BACK (door side)'), (-88, 30, 'FRONT (lens side)'),
                   (-25, 23.5, 'take-up end'), (-149, 23.5, 'rewind end')]:
    ax.text(y, x, text, ha='center', va='center', fontsize=9, color=MUTED)

ax.set_xlim(11.3, -186.8); ax.set_ylim(20, 96); ax.set_aspect('equal')
ax.set_xlabel('Y (mm)', fontsize=10, labelpad=1.75); ax.set_ylabel('X (mm)', fontsize=10)
ax.tick_params(length=3, labelsize=8)
ax.tick_params(axis='x', pad=1.7)
ax.set_title(f'Body, seen from above (cut at z = {Z:.1f} mm, just below the top face)', loc='left',
             fontsize=12, fontweight='bold', color=INK)
save(fig, OUT, DPI)
