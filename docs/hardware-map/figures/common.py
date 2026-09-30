"""Shared setup and drawing helpers for the hardware guide figures, which are drawn from the STEP.

Import it first in a figure script: it puts tools/ on the path, loads the Inter font and sets
the plot style, so `from common import ...` then `from cad import step` both work.
"""
import sys
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
IMG = HERE.parent / 'img'       # figures made for the guide
DOCS = REPO / 'docs'            # figures the README shows too (fig*.png)
sys.path.insert(0, str(REPO / 'tools'))

FONTS = HERE / '.fonts'   # Inter, fetched once and kept out of git
FONT_URL = 'https://cdn.jsdelivr.net/fontsource/fonts/inter@5/latin-{w}-normal.ttf'
INK, EDGE, MUTED = '#121212', '#4a4a4a', '#6b6b6b'
INSERT, PLUNGER = '#0072b2', '#e69f00'   # badge colours for heat-set inserts and ball plungers


def load_fonts():
    FONTS.mkdir(exist_ok=True)
    for w in (400, 700):
        f = FONTS / f'Inter-{w}.ttf'
        if not f.exists():
            urllib.request.urlretrieve(FONT_URL.format(w=w), f)
        fm.fontManager.addfont(str(f))


load_fonts()
plt.rcParams.update({'font.family': 'Inter', 'font.size': 9, 'axes.edgecolor': 'none',
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.labelcolor': MUTED})


def section(mesh, origin, normal, axes):
    """The cut of a trimesh by a plane, as a shapely shape in the two coordinates `axes`
    (e.g. [0, 2] for X and Z). Loops are combined even-odd, so holes stay holes."""
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    out = Polygon()
    if s is None:
        return out
    for e in s.discrete:
        if len(e) > 3:
            out = out.symmetric_difference(Polygon(e[:, axes]).buffer(0))
    return out


def draw(ax, geom, fc, lw=0.8, z=1, ec=EDGE):
    """Fill a shapely shape, with its holes in white."""
    for g in getattr(geom, 'geoms', [geom]):
        if g.is_empty or not hasattr(g, 'exterior'):
            continue
        ax.fill(*g.exterior.xy, fc=fc, ec=ec, lw=lw, zorder=z)
        for h in g.interiors:
            ax.fill(*h.xy, fc='white', ec=ec, lw=lw, zorder=z)


def label(ax, x, y, text, tx, ty, ha='left'):
    """Text at (tx, ty) with a leader line to the point (x, y)."""
    ax.annotate(text, (x, y), (tx, ty), ha=ha, va='center', fontsize=9, color=INK,
                arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=10)


def cylinders(shape, radius, tol=0.005):
    """Every cylindrical face of `radius` in a solid, as the two ends of its axis over the face's
    length (numpy XYZ points). A hole split into half-faces comes back once."""
    out = {}
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        s = BRepAdaptor_Surface(TopoDS.Face(ex.Current()))
        ex.Next()
        if s.GetType() != GeomAbs_Cylinder or abs(s.Cylinder().Radius() - radius) > tol:
            continue
        axis = s.Cylinder().Axis()
        p, d = axis.Location(), axis.Direction()
        p, d = np.array([p.X(), p.Y(), p.Z()]), np.array([d.X(), d.Y(), d.Z()])
        a, b = p + d * s.FirstVParameter(), p + d * s.LastVParameter()
        out[tuple(np.round((a + b) / 2, 2))] = (a, b)
    return list(out.values())


def badge(ax, x, y, text, tx, ty, size=10):
    """A plunger's square orange badge at (tx, ty), with a leader to a dot at (x, y)."""
    ax.annotate('', (x, y), (tx, ty), arrowprops=dict(arrowstyle='-', color=INK, lw=0.9), zorder=8)
    ax.plot(x, y, 'o', ms=4.5, mfc=PLUNGER, mec=INK, mew=0.8, zorder=9)
    ax.text(tx, ty, text, ha='center', va='center', fontsize=size, fontweight='bold', color=INK, zorder=10,
            bbox=dict(boxstyle='square,pad=0.35', fc=PLUNGER, ec=INK, lw=0.9))


def save(fig, out, dpi=200):
    """Write the PNG the same way every time: 200 dpi unless told otherwise, no software stamp."""
    fig.savefig(out, dpi=dpi, metadata={'Software': None})
    print(f'wrote {out.relative_to(REPO)}')


def on_axis(shape, point, direction, tol=0.02):
    """The cylindrical faces of a solid whose axis runs through `point` along `direction` (a unit
    vector), as (diameter, start, end): start < end, measured from `point` along `direction`, in
    order of start. A hole split into half-faces comes back once."""
    out = set()
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        s = BRepAdaptor_Surface(TopoDS.Face(ex.Current()))
        ex.Next()
        if s.GetType() != GeomAbs_Cylinder:
            continue
        axis = s.Cylinder().Axis()
        p, d = axis.Location(), axis.Direction()
        p, d = np.array([p.X(), p.Y(), p.Z()]) - point, np.array([d.X(), d.Y(), d.Z()])
        if abs(abs(d @ direction) - 1) > 1e-6 or np.linalg.norm(p - (p @ direction) * direction) > tol:
            continue
        a, b = sorted((p + d * v) @ direction for v in (s.FirstVParameter(), s.LastVParameter()))
        out.add((round(2 * s.Cylinder().Radius(), 4), round(a, 4), round(b, 4)))
    return sorted(out, key=lambda c: c[1])
