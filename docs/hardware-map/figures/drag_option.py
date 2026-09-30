"""Figure 11 of the hardware guide: the drag option from above and cut through P7.

Drawn from the STEP, so rerun it after any change to the drag cover, the drag counter face
or the counter gear: mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from shapely.affinity import translate
from shapely.geometry import Polygon

import common
from common import EDGE, IMG, INK, draw, label, save
from cad import step  # noqa: E402

OUT = IMG / 'drag-option.png'
NAMES = ['drag-cover', 'drag-counter-face', 'counter-gear']
M = {n: step.tessellate(s, 0.003, 0.03) for n, s in step.load_solids(names=set(NAMES)).items()}
FILL = {'drag-cover': '#e3e3e3', 'drag-counter-face': '#d6d6d6', 'counter-gear': '#c8d3dc', 'body-solid': '#efefef'}
DIAL = np.array([67.69, -63.95])
P7Z = 48.15
# P7 pushes the face and the counter gear across until the face's skirt meets the cover
# step on the far side; both views draw them in that fitted position
FLOAT = 0.14


def section(name, origin, normal, axes):
    return common.section(M[name], origin, normal, axes)


def badge(ax, x, y, text, tx, ty):
    ax.annotate('', (x, y), (tx, ty), arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=8)
    ax.plot(x, y, 'o', ms=4.5, mfc='#e69f00', mec=INK, mew=0.8, zorder=9)
    ax.text(tx, ty, text, ha='center', va='center', fontsize=10, fontweight='bold', color=INK, zorder=10,
            bbox=dict(boxstyle='square,pad=0.35', fc='#e69f00', ec=INK, lw=0.9))


fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw={'width_ratios': [1, 1.25]})

# ---- plan view: the drag cover's top at the dial, the face over it
top = section('drag-cover', [0, 0, 50.3], [0, 0, 1], [0, 1])
mid = section('drag-cover', [0, 0, 47.0], [0, 0, 1], [0, 1])
face = translate(section('drag-counter-face', [0, 0, 48.6], [0, 0, 1], [0, 1]), FLOAT)
win = Polygon([(46, -80), (86, -80), (86, -47), (46, -47)])
draw(a1, mid.intersection(win), FILL['drag-cover'])
draw(a1, face, FILL['drag-counter-face'], z=2)
draw(a1, top, '#cfcfcf', z=3)
# P7's line of action, and the triangle marker five frames round from it
a1.plot([54.435, 57.63], [-63.94, -63.94], color='#e69f00', lw=3, solid_capstyle='butt', zorder=5)
tri = section('drag-cover', [0, 0, 47.15], [0, 0, 1], [0, 1]).intersection(Polygon([(59, -57), (70, -57), (70, -47.5), (59, -47.5)]))
for g in getattr(tri, 'geoms', [tri]):
    for h in getattr(g, 'interiors', []):
        a1.fill(*h.xy, fc='white', ec=INK, lw=0.8, zorder=4)
a1.plot(*DIAL, '+', color=EDGE, ms=8, zorder=5)
for k in (0, 5):  # radial lines at the marker (108 deg) and at P7 (180 deg)
    ang = np.radians(108 + 14.4 * k)
    a1.plot([DIAL[0] + 3 * np.cos(ang), DIAL[0] + 9.5 * np.cos(ang)], [DIAL[1] + 3 * np.sin(ang), DIAL[1] + 9.5 * np.sin(ang)],
            color=EDGE, lw=0.6, ls=(0, (3, 2)), zorder=5)
a1.text(DIAL[0] - 3.2, DIAL[1] + 2.6, '72°\n5 frames', ha='center', va='center', fontsize=8, color=EDGE, zorder=6)
label(a1, 63.6, -52.2, 'triangle marker', 50.0, -52.0)
label(a1, 72.0, -58.0, 'drag-counter-face,\na detent flute under\nevery frame', 73.5, -50.0)
label(a1, 80.0, -70.5, 'drag-cover', 79.0, -77.5, ha='left')
badge(a1, 56.3, -63.94, 'P7', 50.0, -73.0)
a1.set_xlim(46, 86); a1.set_ylim(-80, -47); a1.set_aspect('equal')
a1.set_xticks([]); a1.set_yticks([])
a1.set_title('From above, lens side on the left', loc='left', fontsize=9, color='#6b6b6b')

# ---- cut through P7 and the dial axis
for n in ['counter-gear', 'drag-cover', 'drag-counter-face']:
    cut = section(n, [0, DIAL[1], 0], [0, 1, 0], [0, 2])
    draw(a2, cut if n == 'drag-cover' else translate(cut, FLOAT), FILL[n])
# plunger: flange in its seat, body in the hole, ball pressed into the groove
seat_floor, hole_end, flange_face = 57.235, 54.435, 57.73  # flange 0.1 proud of the tower face
a2.add_patch(Rectangle((seat_floor, P7Z - 1.25), flange_face - seat_floor, 2.5, fc='#e69f00', ec=INK, lw=0.8, zorder=5))
a2.add_patch(Rectangle((hole_end + 0.25, P7Z - 1.0), seat_floor - hole_end - 0.25, 2.0, fc='#e69f00', ec=INK, lw=0.8, zorder=5))
rim = DIAL[0] + FLOAT - 10.0
a2.add_patch(Circle((rim - 0.75, P7Z), 0.75, fc='#bdbdbd', ec=INK, lw=0.8, zorder=6))
label(a2, 58.0, 49.9, 'tower on drag-cover,\n0.2 mm clear of the rim', 54.0, 51.6, ha='center')
label(a2, 57.87, 48.05, 'plain rim, with a 120° V-flute\nunder every frame', 61.0, 51.0)
label(a2, 64.0, 49.2, 'drag-counter-face', 67.2, 49.9)
label(a2, 62.0, 44.5, 'counter gear', 64.0, 43.2)
badge(a2, 55.5, P7Z, 'P7', 51.2, 45.2)
a2.set_xlim(49.5, 70.5); a2.set_ylim(42.5, 52.2); a2.set_aspect('equal')
a2.set_xlabel('X (mm)'); a2.set_ylabel('Z (mm)')
a2.tick_params(length=3)
a2.set_title('Cut through P7 and the dial axis', loc='left', fontsize=9, color='#6b6b6b')

fig.suptitle('Drag option: P7 presses a ball on the counter face rim', x=0.02, ha='left', fontsize=13, fontweight='bold', color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.95))
save(fig, OUT)
