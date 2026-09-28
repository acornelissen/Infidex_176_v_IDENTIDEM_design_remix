"""Figure 11 of the hardware guide: the drag option from above and cut through P7.

Drawn from the STEP, so rerun it after any change to the drag cover, the drag counter face
or the counter gear: mise run figures
"""
import sys
import urllib.request
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, Circle
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'tools'))
from cad import step  # noqa: E402

OUT = HERE.parent / 'img' / 'drag-option.png'
FONTS = HERE / '.fonts'   # Inter, fetched once and kept out of git
FONT_URL = 'https://cdn.jsdelivr.net/fontsource/fonts/inter@5/latin-{w}-normal.ttf'


def load_fonts():
    FONTS.mkdir(exist_ok=True)
    for w in (400, 700):
        f = FONTS / f'Inter-{w}.ttf'
        if not f.exists():
            urllib.request.urlretrieve(FONT_URL.format(w=w), f)
        fm.fontManager.addfont(str(f))


load_fonts()
plt.rcParams.update({'font.family': 'Inter', 'font.size': 9, 'axes.edgecolor': 'none',
                     'xtick.color': '#6b6b6b', 'ytick.color': '#6b6b6b', 'axes.labelcolor': '#6b6b6b'})
NAMES = ['drag-cover', 'drag-counter-face', 'counter-gear']
M = {n: step.tessellate(s, 0.003, 0.03) for n, s in step.load_solids(names=set(NAMES)).items()}
INK, EDGE = '#121212', '#4a4a4a'
FILL = {'drag-cover': '#e3e3e3', 'drag-counter-face': '#d6d6d6', 'counter-gear': '#c8d3dc', 'body-solid': '#efefef'}
DIAL = np.array([67.69, -63.95])
P7Z = 48.15


def section(name, origin, normal, axes):
    s = M[name].section(plane_origin=origin, plane_normal=normal)
    polys = [Polygon(e[:, axes]) for e in s.discrete if len(e) > 3]
    out = Polygon()
    for p in polys:  # even-odd fill
        out = out.symmetric_difference(p.buffer(0))
    return out


def draw(ax, geom, fc, lw=0.8, z=1):
    for g in getattr(geom, 'geoms', [geom]):
        if g.is_empty:
            continue
        ax.fill(*g.exterior.xy, fc=fc, ec=EDGE, lw=lw, zorder=z)
        for h in g.interiors:
            ax.fill(*h.xy, fc='white', ec=EDGE, lw=lw, zorder=z)


def badge(ax, x, y, text, tx, ty):
    ax.annotate('', (x, y), (tx, ty), arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=8)
    ax.plot(x, y, 'o', ms=4.5, mfc='#e69f00', mec=INK, mew=0.8, zorder=9)
    ax.text(tx, ty, text, ha='center', va='center', fontsize=10, fontweight='bold', color=INK, zorder=10,
            bbox=dict(boxstyle='square,pad=0.35', fc='#e69f00', ec=INK, lw=0.9))


def label(ax, x, y, text, tx, ty, ha='left'):
    ax.annotate(text, (x, y), (tx, ty), ha=ha, va='center', fontsize=9, color=INK,
                arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=10)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw={'width_ratios': [1, 1.25]})

# ---- plan view: the drag cover's top at the dial, the face over it
top = section('drag-cover', [0, 0, 50.3], [0, 0, 1], [0, 1])
mid = section('drag-cover', [0, 0, 47.0], [0, 0, 1], [0, 1])
face = section('drag-counter-face', [0, 0, 48.6], [0, 0, 1], [0, 1])
win = Polygon([(46, -80), (86, -80), (86, -47), (46, -47)])
draw(a1, mid.intersection(win), FILL['drag-cover'])
draw(a1, face, FILL['drag-counter-face'], z=2)
draw(a1, top, '#cfcfcf', z=3)
# P7's line of action, and the triangle marker five frames round from it
a1.plot([54.295, 57.49], [-63.94, -63.94], color='#e69f00', lw=3, solid_capstyle='butt', zorder=5)
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
    draw(a2, section(n, [0, DIAL[1], 0], [0, 1, 0], [0, 2]), FILL[n])
# plunger: flange in its seat, body in the hole, ball pressed into the groove
seat_floor, hole_end, flange_face = 57.095, 54.295, 57.59  # flange 0.1 proud of the tower face
a2.add_patch(Rectangle((seat_floor, P7Z - 1.25), flange_face - seat_floor, 2.5, fc='#e69f00', ec=INK, lw=0.8, zorder=5))
a2.add_patch(Rectangle((hole_end + 0.25, P7Z - 1.0), seat_floor - hole_end - 0.25, 2.0, fc='#e69f00', ec=INK, lw=0.8, zorder=5))
groove_bottom = DIAL[0] - 9.88
a2.add_patch(Circle((groove_bottom - 0.75, P7Z), 0.75, fc='#bdbdbd', ec=INK, lw=0.8, zorder=6))
label(a2, 58.0, 49.9, 'tower on drag-cover,\n0.2 mm clear of the rim', 54.0, 51.6, ha='center')
label(a2, 57.87, 48.05, 'ball groove, 0.12 mm deep;\nflutes 0.3 mm deeper', 61.0, 51.0)
label(a2, 64.0, 49.2, 'drag-counter-face', 67.2, 49.9)
label(a2, 62.0, 44.5, 'counter gear', 64.0, 43.2)
badge(a2, 55.5, P7Z, 'P7', 51.2, 45.2)
a2.set_xlim(49.5, 70.5); a2.set_ylim(42.5, 52.2); a2.set_aspect('equal')
a2.set_xlabel('X (mm)'); a2.set_ylabel('Z (mm)')
a2.tick_params(length=3)
a2.set_title('Cut through P7 and the dial axis', loc='left', fontsize=9, color='#6b6b6b')

fig.suptitle('Drag option: P7 presses a ball on the counter face rim', x=0.02, ha='left', fontsize=13, fontweight='bold', color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(OUT, dpi=200, metadata={'Software': None})
print(f'wrote {OUT.relative_to(REPO)}')
