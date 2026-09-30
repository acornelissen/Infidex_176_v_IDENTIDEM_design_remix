"""Figure 8 of the hardware guide: the counter face on the counter gear, cut through the dial axis.

Drawn from the STEP, so rerun it after any change to the counter face or the counter gear:
mise run figures
"""
import sys
import urllib.request
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'tools'))
from cad import step  # noqa: E402

OUT = HERE.parent / 'img' / 'counter-face.png'
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
NAMES = ['simple-counter-face', 'counter-gear']
M = {n: step.tessellate(s, 0.003, 0.03) for n, s in step.load_solids(names=set(NAMES)).items()}
INK, EDGE, MUTED = '#121212', '#4a4a4a', '#6b6b6b'
FILL = {'simple-counter-face': '#d9d9d9', 'counter-gear': '#c8d3dc'}
HUB = np.array([67.704, -63.939])   # the counter gear's hub axis; a dog tooth sits on +X from it

# S13 (M2×4 thumbscrew) and I12 (M2 insert), drawn as blocks: the head in the face's
# Ø6.0 × 0.5 recess, the shank down to the face's underside, the insert in the hub's Ø3.2 hole
HEAD_D, HEAD_Z0, HEAD_Z1 = 5.5, 48.9, 50.5
SHANK_D, SHANK_Z0 = 2.0, 44.9
INSERT_D, INSERT_Z0, INSERT_Z1 = 3.2, 44.0, 48.0


def section(name):
    s = M[name].section(plane_origin=[0, HUB[1], 0], plane_normal=[0, 1, 0])
    polys = [Polygon(e[:, [0, 2]]) for e in s.discrete if len(e) > 3]
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


def label(ax, x, y, text, tx, ty, ha='left'):
    ax.annotate(text, (x, y), (tx, ty), ha=ha, va='center', fontsize=9, color=INK,
                arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=10)


fig, ax = plt.subplots(figsize=(5.45, 3.11))
for n in NAMES:
    draw(ax, section(n), FILL[n])

cx = HUB[0]
ax.add_patch(Rectangle((cx - INSERT_D / 2, INSERT_Z0), INSERT_D, INSERT_Z1 - INSERT_Z0, fc='#c9a227', ec=INK,
                       lw=0.8, hatch='///', zorder=3))
ax.add_patch(Rectangle((cx - SHANK_D / 2, SHANK_Z0), SHANK_D, HEAD_Z0 - SHANK_Z0, fc='#7f8a93', ec=INK, lw=0.8, zorder=4))
ax.add_patch(Rectangle((cx - HEAD_D / 2, HEAD_Z0), HEAD_D, HEAD_Z1 - HEAD_Z0, fc='#7f8a93', ec=INK, lw=0.8, zorder=4))

label(ax, cx + HEAD_D / 2, HEAD_Z1, 'S13  M2×4 thumbscrew', 72.0, 51.8)
ax.annotate('', (cx - INSERT_D / 2, 44.6), (63.0, 42.9), arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=8)
ax.plot(cx - INSERT_D / 2, 44.6, 'o', ms=4.5, mfc='#0072b2', mec=INK, mew=0.8, zorder=9)
ax.text(63.0, 42.9, 'I12', ha='center', va='center', fontsize=10, fontweight='bold', color='white', zorder=10,
        bbox=dict(boxstyle='circle,pad=0.3', fc='#0072b2', ec=INK, lw=0.9))
dog_x = HUB[0] + 8.45
label(ax, dog_x, 45.4, 'dog tooth in a notch', 74.6, 42.8, ha='center')
ax.text(58.3, 49.75, 'counter face', fontsize=9, color=MUTED, zorder=6)
ax.text(58.3, 44.55, 'counter gear', fontsize=9, color=MUTED, zorder=6)

ax.set_xlim(57.5, 77.9); ax.set_ylim(42.2, 52.3); ax.set_aspect('equal')
ax.set_xlabel('X (mm)'); ax.set_ylabel('Z (mm)')
ax.tick_params(length=3)
ax.set_title('Counter face on the counter gear, cut through the dial axis', loc='left', fontsize=11,
             fontweight='bold', color=INK)
fig.tight_layout()
fig.savefig(OUT, dpi=200, metadata={'Software': None})
print(f'wrote {OUT.relative_to(REPO)}')
