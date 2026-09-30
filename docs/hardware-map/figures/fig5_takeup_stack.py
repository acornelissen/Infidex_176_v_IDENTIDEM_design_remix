"""Figure 6 of the hardware guide (docs/fig5_takeup_stack.png, which the README shows too): the take-up
axis cut front to back, with knob screw S12 in insert I13, magnet M1 above the M2/M3 stack in the
spool head, and collar C1 in the spool's groove.

The screw, insert and magnets are bought, so they are drawn as blocks from the README's sizes, placed
in their holes and pockets as the STEP has them.

Drawn from the STEP, so rerun it after any change to the advance knob, the inner-ratchet, the take-up
spool, the collar, the top cover or the body: mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Polygon, Rectangle

import common
from common import DOCS, EDGE, INK, INSERT, draw, on_axis, save
from cad import step  # noqa: E402

OUT = DOCS / 'fig5_takeup_stack.png'
AXIS = np.array([64.0, -25.0, 0.0])   # the take-up axis, X and Y
UP = np.array([0.0, 0.0, 1.0])
# the cut, a hair behind the centre: exactly on it the plane grazes an edge in the body and the section breaks up
CUT = AXIS + [0, -0.005, 0]
PARTS = {   # STEP solid: (legend name, fill), drawn in this order
    'body-solid': ('body', '#ececec'),
    'simple-cover': ('top cover', '#d9d9d9'),
    'advance-knob': ('advance knob', '#dde5d8'),
    'inner-ratchet': ('inner-ratchet', '#d8cfc0'),
    'take-up-spool': ('take-up spool', '#c9d3dc'),
    'takeup-washer-stopper': ('spool collar', '#f0c7a0'),
}
LARGE = {'body-solid', 'simple-cover'}   # slow to mesh finely
MAGNET, BRASS, STEEL = '#009e73', '#c9a227', '#7f8a93'

# bought parts: S12 M2×6 flat head (Ø3.8 at 90°, length taken from the top of the head),
# I13 M2 × 4 insert, M1 Ø5 × 2 and M2, M3 Ø4 × 2 magnets
HEAD_D, SHANK_D, SCREW_L = 3.8, 2.0, 6.0
INSERT_D = 3.2   # drawn filling its hole
M1_D, M1_T, STACK_D, STACK_T = 5.0, 2.0, 4.0, 2.0

S = step.load_solids(names=set(PARTS))
M = {n: step.tessellate(s, 0.01, 0.1) if n in LARGE else step.tessellate(s, 0.005, 0.05) for n, s in S.items()}


def hole(name, diameter):
    """(start Z, end Z) of the part's cylinder of `diameter` on the take-up axis."""
    for d, z0, z1 in on_axis(S[name], AXIS, UP):
        if abs(d - diameter) < 0.01:
            return z0, z1
    raise ValueError(f'no Ø{diameter} on the take-up axis in {name}')


m1_pocket = hole('inner-ratchet', 5.1)        # from below; M1 is pressed to its floor
insert_hole = hole('inner-ratchet', INSERT_D)   # I13, open into the M1 pocket
stack_pocket = hole('take-up-spool', 4.1)     # M2 at its bottom, M3 on top
knob_face = hole('advance-knob', 7.0)[0]      # floor of the knob's well, where the S12 countersink opens
head_top = knob_face + (HEAD_D - 3.7) / 2     # a Ø3.8 head in the Ø3.7 countersink stands a hair proud
m1 = (m1_pocket[1] - M1_T, m1_pocket[1])
m2 = (stack_pocket[0], stack_pocket[0] + STACK_T)
m3 = (m2[1], m2[1] + STACK_T)

plt.rcParams['font.size'] = 7.8
fig, ax = plt.subplots(figsize=(5.165, 6.305))
fig.subplots_adjust(left=0.0803, right=0.9748, bottom=0.1792, top=0.9508)
for n, (_, fill) in PARTS.items():
    draw(ax, common.section(M[n], CUT, [0, 1, 0], [0, 2]), fill, lw=0.7)

cx = AXIS[0]


def block(d, z, fc, **kw):
    ax.add_patch(Rectangle((cx - d / 2, z[0]), d, z[1] - z[0], fc=fc, ec=INK, lw=0.8, zorder=4, **kw))


def magnet_badge(z, text, tx, ty):
    """Leader from the magnet's centre, under the magnet, to a green badge."""
    y = (z[0] + z[1]) / 2
    ax.plot([cx, tx], [y, ty], color=INK, lw=0.8, zorder=3)
    ax.plot(cx, y, 'o', ms=4, mfc='none', mec=INK, mew=0.8, zorder=5)
    ax.text(tx, ty, text, ha='center', va='center', fontsize=8.7, fontweight='bold', color='white', zorder=10,
            bbox=dict(boxstyle='round,pad=0.3', fc=MAGNET, ec=INK, lw=0.8))


block(INSERT_D, insert_hole, BRASS, hatch='///')
block(M1_D, m1, MAGNET)
block(STACK_D, m2, MAGNET)
block(STACK_D, m3, MAGNET)
h = (HEAD_D - SHANK_D) / 2   # height of the 90° head
tip = head_top - SCREW_L
ax.add_patch(Polygon([(cx - HEAD_D / 2, head_top), (cx + HEAD_D / 2, head_top), (cx + SHANK_D / 2, head_top - h),
                      (cx + SHANK_D / 2, tip), (cx - SHANK_D / 2, tip), (cx - SHANK_D / 2, head_top - h)],
                     fc=STEEL, ec=INK, lw=0.8, zorder=5))

leader = dict(arrowstyle='-', color=INK, lw=0.8)
ax.annotate('S12  M2×6 countersunk', (cx, head_top), (52.5, 51.7), va='center', fontsize=7.2, color=INK,
            arrowprops=leader, zorder=10)
ax.annotate('C1  split collar', (69.6, 32.2), (72.5, 30.4), va='center', fontsize=7.2, color=INK, arrowprops=leader,
            zorder=10)
dot = (cx + 1.4, insert_hole[1] - 1.5)
ax.plot([dot[0], 74.0], [dot[1], 44.8], color=INK, lw=0.8, zorder=8)
ax.plot(*dot, 'o', ms=4, mfc=INSERT, mec=INK, mew=0.8, zorder=9)
ax.text(74.0, 44.8, 'I13', ha='center', va='center', fontsize=8.7, fontweight='bold', color='white', zorder=10,
        bbox=dict(boxstyle='circle,pad=0.3', fc=INSERT, ec=INK, lw=0.8))
magnet_badge(m1, 'M1', 74.0, 39.2)
magnet_badge(m3, 'M3', 74.0, 36.35)
magnet_badge(m2, 'M2', 54.0, 33.2)

handles = [Patch(fc=fill, ec=EDGE, lw=0.7, label=name) for name, fill in
           [PARTS[n] for n in ('advance-knob', 'simple-cover', 'inner-ratchet', 'takeup-washer-stopper',
                               'take-up-spool', 'body-solid')]]
handles += [Patch(fc=MAGNET, ec=INK, lw=0.8, label='magnet'), Patch(fc=BRASS, ec=INK, lw=0.8, hatch='///', label='heat-set insert'),
            Patch(fc=STEEL, ec=INK, lw=0.8, label='screw')]
fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.527, 0.104), ncol=3, frameon=False,
           labelspacing=0.25, handleheight=0.6)

ax.set_xlim(50, 80); ax.set_ylim(26, 57.6); ax.set_aspect('equal')
ax.set_xlabel('X (mm)', labelpad=1); ax.set_ylabel('Z (mm)')
ax.tick_params(length=3, labelsize=6.2, pad=2)
ax.set_title('Take-up axis, cut front to back through the centre', loc='left', fontsize=9.6, fontweight='bold',
             color=INK, pad=9)
save(fig, OUT)
