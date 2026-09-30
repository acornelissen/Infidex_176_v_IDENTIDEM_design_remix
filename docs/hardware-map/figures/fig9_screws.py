"""Figure 9 of the README (Figure 7 of the hardware guide): the screws seated in their inserts,
cut through S1, S6, S8 and S14.

The printed parts are cut from the STEP; the screws and inserts are bought parts, drawn as
blocks from their standard sizes and placed on the seats and holes found in the STEP. Rerun it
after any change to the body, the top cover, the cold shoe, the lens standard (helicoid-mount),
the sprocket or the sprocket gear (ratchet-coupling-gear): mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Rectangle
from shapely.affinity import translate
from shapely.geometry import Point, Polygon

import common
from common import DOCS, INK, MUTED, draw, save
from cad import step  # noqa: E402

OUT = DOCS / 'fig9_screws.png'
BIG = {'body-solid', 'simple-cover'}   # slow to mesh at the fine tolerance
NAMES = BIG | {'cold-shoe', 'helicoid-mount', 'sprocket', 'ratchet-coupling-gear'}
M = {n: step.tessellate(s, *((0.01, 0.1) if n in BIG else (0.003, 0.03)))
     for n, s in step.load_solids(names=NAMES).items()}
FILL = {'body-solid': '#ebebeb', 'simple-cover': '#d9d9d9', 'cold-shoe': '#d9d9d9', 'helicoid-mount': '#d9d9d9',
        'ratchet-coupling-gear': '#d9d9d9', 'sprocket': '#c8d3dc'}
SCREW, INSERT = '#7f8a93', '#c9a227'
plt.rcParams['font.size'] = 8   # four panels side by side: a size smaller than the other figures

INSERT_LEN = 4.0     # every insert is 4 mm long, pressed flush with the face
COVER_DROP = 0.1     # the top cover seats this far below its drawn height once screwed down
# the insert positions from the guide's table; each is snapped to its hole in the STEP
I1, I6, I8, I14 = (53.4, -9.1), (56.4, -98.8), (-52.2, 35.3), (73.2, -45.2)


def section(name, origin, normal, axes):
    return common.section(M[name], origin, normal, axes)


def hole(name, origin, normal, axes, near):
    """(centre, diameter) of the round hole in a cut of `name` nearest the point `near`."""
    cut = section(name, origin, normal, axes)
    rings = [Polygon(h) for g in getattr(cut, 'geoms', [cut]) for h in getattr(g, 'interiors', [])]
    ring = min(rings, key=lambda r: r.centroid.distance(Point(near)))
    return np.array(ring.centroid.coords[0]), 2 * np.sqrt(ring.area / np.pi)


def hit(name, origin, direction):
    """Where a ray from `origin` first meets `name`, as a distance along `direction`."""
    loc, _, _ = M[name].ray.intersects_location([origin], [direction])
    return min(np.dot(p - origin, direction) for p in loc)


def blocks(ax, c, top, sign, head, d, length, flip=False):
    """A screw drawn as blocks. Its axis is at `c` across the cut and its head top at `top`;
    it points in the direction `sign` (+1 or -1) along the axis. `head` is ('csk', dk) for a
    90° countersunk head or ('cap', dk, k). `flip` puts the axis along x instead of y."""
    def pts(p):
        p = [(c + v, top + sign * u) for v, u in p]
        return [(y, x) for x, y in p] if flip else p
    if head[0] == 'csk':
        k = (head[1] - d) / 2
        outline = [(-head[1] / 2, 0), (head[1] / 2, 0), (d / 2, k), (d / 2, length), (-d / 2, length), (-d / 2, k)]
        ax.add_patch(Patch(pts(outline), fc=SCREW, ec=INK, lw=0.8, zorder=4))
    else:
        dk, k = head[1], head[2]
        ax.add_patch(Patch(pts([(-dk / 2, 0), (dk / 2, 0), (dk / 2, k), (-dk / 2, k)]), fc=SCREW, ec=INK, lw=0.8, zorder=4))
        ax.add_patch(Patch(pts([(-d / 2, k), (d / 2, k), (d / 2, k + length), (-d / 2, k + length)]), fc=SCREW, ec=INK,
                           lw=0.8, zorder=4))


def insert(ax, c, face, sign, dia, flip=False):
    """An insert pressed flush into `face`, filling a hole of diameter `dia`."""
    lo, hi = sorted((face, face + sign * INSERT_LEN))
    xy, w, h = ((lo, c - dia / 2), hi - lo, dia) if flip else ((c - dia / 2, lo), dia, hi - lo)
    ax.add_patch(Rectangle(xy, w, h, fc=INSERT, ec=INK, lw=0.8, hatch='///', zorder=3))


def finish(ax, title, xl, yl, xlabel, ylabel):
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_aspect('equal')
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.tick_params(length=3)
    ax.set_title(title, loc='left', fontsize=10, fontweight='bold', color=INK)


fig, axs = plt.subplots(1, 4, figsize=(14.295, 3.595), gridspec_kw={'width_ratios': [0.96, 0.98, 1.26, 1.05]})

# ---- S1-S5: M2x6 countersunk through the top cover into I1, cover screwed down
ax = axs[0]
(x, y), dia = hole('body-solid', [0, 0, 39], [0, 0, 1], [0, 1], I1)
face_z = 60 - hit('body-solid', [x + 3.0, y, 60], [0, 0, -1])
top = 60 - hit('simple-cover', [x + 3.0, y, 60], [0, 0, -1]) - COVER_DROP
draw(ax, section('body-solid', [0, y, 0], [0, 1, 0], [0, 2]), FILL['body-solid'])
draw(ax, translate(section('simple-cover', [0, y, 0], [0, 1, 0], [0, 2]), 0, -COVER_DROP), FILL['simple-cover'])
insert(ax, x, face_z, -1, dia)
blocks(ax, x, top, -1, ('csk', 3.8), 2.0, 6.0)
ax.text(x - 3.75, top + 0.75, 'top cover', color=MUTED, zorder=6)
ax.text(x - 3.75, face_z - 5.6, 'body', color=MUTED, zorder=6)
finish(ax, 'S1–S5  M2×6 countersunk', (x - 4.0, x + 5.1), (face_z - 6.1, face_z + 3.4), 'X (mm)', 'Z (mm)')

# ---- S6-S7: M2x4 countersunk through the cold shoe into I6
ax = axs[1]
(x, y), dia = hole('body-solid', [0, 0, 40], [0, 0, 1], [0, 1], I6)
face_z = 60 - hit('body-solid', [x + 3.0, y, 60], [0, 0, -1])
top = 60 - hit('cold-shoe', [x + 3.0, y, 60], [0, 0, -1])
for n in ('body-solid', 'cold-shoe'):
    draw(ax, section(n, [0, y, 0], [0, 1, 0], [0, 2]), FILL[n])
insert(ax, x, face_z, -1, dia)
blocks(ax, x, top, -1, ('csk', 3.8), 2.0, 4.0)
ax.text(x + 2.4, top + 0.7, 'cold shoe', color=MUTED, zorder=6)
ax.text(x - 4.4, face_z - 5.5, 'body', color=MUTED, zorder=6)
finish(ax, 'S6–S7  M2×4 countersunk', (x - 5.0, x + 5.0), (face_z - 6.13, face_z + 4.1), 'X (mm)', '')

# ---- S8-S11: M3x4 cap through the lens standard into I8, cut across at I8's height
ax = axs[2]
(y, z), dia = hole('body-solid', [51, 0, 0], [1, 0, 0], [1, 2], I8)
face_x = hit('body-solid', [0, y, z + 4.0], [1, 0, 0])
seat = hit('helicoid-mount', [30, y + 2.4, z], [1, 0, 0]) + 30   # counterbore floor
for n in ('body-solid', 'helicoid-mount'):
    draw(ax, section(n, [0, 0, z], [0, 0, 1], [0, 1]), FILL[n])
insert(ax, y, face_x, +1, dia, flip=True)
blocks(ax, y, seat - 3.0, +1, ('cap', 5.5, 3.0), 3.0, 4.0, flip=True)
ax.text(face_x - 6.5, y + 4.5, 'lens standard', color=MUTED, zorder=6)
ax.text(face_x + 4.4, y + 4.5, 'body', color=MUTED, zorder=6)
finish(ax, 'S8–S11  M3×4 cap (or countersunk)', (face_x - 7.07, face_x + 6.94), (y - 5.8, y + 5.3),
       'X (mm), lens side on the left', 'Y (mm)')

# ---- S14: M2x6 cap through the sprocket gear into I14
ax = axs[3]
(x, y), dia = hole('sprocket', [0, 0, 28], [0, 0, 1], [0, 1], I14)
face_z = 60 - hit('sprocket', [x + 2.5, y, 60], [0, 0, -1])
seat = 60 - hit('ratchet-coupling-gear', [x + 1.5, y, 60], [0, 0, -1])   # counterbore floor
for n in ('sprocket', 'ratchet-coupling-gear'):
    draw(ax, section(n, [0, y, 0], [0, 1, 0], [0, 2]), FILL[n])
insert(ax, x, face_z, -1, dia)
blocks(ax, x, seat + 2.0, -1, ('cap', 3.8, 2.0), 2.0, 6.0)
ax.text(x - 4.8, face_z + 3.8, 'sprocket gear', color=MUTED, zorder=6)
ax.text(x - 4.8, face_z - 4.7, 'sprocket', color=MUTED, zorder=6)
finish(ax, 'S14  M2×6 cap or countersunk', (x - 5.0, x + 5.0), (face_z - 5.0, face_z + 4.5), 'X (mm)', 'Z (mm)')

fig.tight_layout(w_pad=2.0)
save(fig, OUT)
