"""Figure 9 of the hardware guide: collar C1 (takeup-washer-stopper) in the take-up spool's groove, from above.

Drawn from the STEP, so rerun it after any change to the collar or the take-up spool:
mise run figures
"""
import matplotlib.pyplot as plt

import common
from common import IMG, INK, MUTED, draw, save
from cad import step  # noqa: E402

OUT = IMG / 'collar.png'
NAMES = ['takeup-washer-stopper', 'take-up-spool']
M = {n: step.tessellate(s, 0.003, 0.03) for n, s in step.load_solids(names=set(NAMES)).items()}
FILL = {'takeup-washer-stopper': '#f0c7a0', 'take-up-spool': '#c9d3dc'}
AXIS = (64.0, -25.0)                                  # take-up axis, X and Y
Z = M['takeup-washer-stopper'].bounds[:, 2].mean()    # halfway up the collar, so the spool is cut in its groove


def section(name):
    return common.section(M[name], [0, 0, Z], [0, 0, 1], [1, 0])   # Y across, X up


plt.rcParams['font.size'] = 7.8
fig, ax = plt.subplots(figsize=(4.26, 4.64))
fig.subplots_adjust(left=0.097, right=0.983, bottom=0.083, top=0.941)
draw(ax, section('takeup-washer-stopper'), FILL['takeup-washer-stopper'], lw=0.6)
draw(ax, section('take-up-spool'), FILL['take-up-spool'], lw=0.6, z=2)

x, y = AXIS
ax.text(y, x, 'spool\nbarrel', ha='center', va='center', fontsize=7.2, linespacing=1.0, color=INK, zorder=5)
ax.text(y, 56.1, 'FRONT (lens side)', ha='center', va='center', fontsize=6.6, color=MUTED)
ax.annotate('split', (y + 0.1, 58.3), (y + 5.8, 55.13), ha='center', va='center', fontweight='bold', color=INK,
            annotation_clip=False, arrowprops=dict(arrowstyle='->', color=INK, lw=0.9), zorder=10)

ax.set_xlim(y + 8, y - 8); ax.set_ylim(55.45, 72.4); ax.set_aspect('equal')   # seen from above, Y runs right to left
ax.set_xticks(range(-18, -33, -2)); ax.set_yticks(range(56, 73, 2))
ax.set_xlabel('Y (mm)'); ax.set_ylabel('X (mm)')
ax.tick_params(length=3, labelsize=6.2, pad=2.5)
ax.set_title('Collar C1 in the spool groove, from above', loc='left', fontsize=9.6, fontweight='bold', color=INK)
save(fig, OUT)
