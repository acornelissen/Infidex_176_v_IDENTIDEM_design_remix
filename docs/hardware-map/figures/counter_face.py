"""Figure 8 of the hardware guide: the counter face on the counter gear, cut through the dial axis.

Drawn from the STEP, so rerun it after any change to the counter face or the counter gear:
mise run figures
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import common
from common import IMG, INK, MUTED, draw, label, save
from cad import step  # noqa: E402

OUT = IMG / 'counter-face.png'
NAMES = ['simple-counter-face', 'counter-gear']
M = {n: step.tessellate(s, 0.003, 0.03) for n, s in step.load_solids(names=set(NAMES)).items()}
FILL = {'simple-counter-face': '#d9d9d9', 'counter-gear': '#c8d3dc'}
HUB = np.array([67.704, -63.939])   # the counter gear's hub axis

# S13 (M2×4 thumbscrew) and I12 (M2 insert), drawn as blocks: the head in the face's
# Ø6.0 × 0.5 recess, the shank down to the face's underside, the insert in the hub's Ø3.2 hole
HEAD_D, HEAD_Z0, HEAD_Z1 = 5.5, 48.9, 50.5
SHANK_D, SHANK_Z0 = 2.0, 44.9
INSERT_D, INSERT_Z0, INSERT_Z1 = 3.2, 44.0, 48.0


def section(name):
    return common.section(M[name], [0, HUB[1], 0], [0, 1, 0], [0, 2])


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
ax.text(58.3, 49.75, 'counter face', fontsize=9, color=MUTED, zorder=6)
ax.text(58.3, 44.55, 'counter gear', fontsize=9, color=MUTED, zorder=6)

ax.set_xlim(57.5, 77.9); ax.set_ylim(42.2, 52.3); ax.set_aspect('equal')
ax.set_xlabel('X (mm)'); ax.set_ylabel('Z (mm)')
ax.tick_params(length=3)
ax.set_title('Counter face on the counter gear, cut through the dial axis', loc='left', fontsize=11,
             fontweight='bold', color=INK)
fig.tight_layout()
save(fig, OUT)
