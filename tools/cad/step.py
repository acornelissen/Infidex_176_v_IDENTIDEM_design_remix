"""Read named solids from the STEP and turn them into meshes."""
import subprocess
import tempfile

import numpy as np
import trimesh
from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

from . import INLAY, INLAY_BODY, REPO, STEP, STEP_PATH


def load_solids(path=STEP, names=None):
    """{solid name: shape} for every solid in the STEP, or only those in `names`."""
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != 1:
        raise OSError(f"cannot read STEP file {path}")
    reader.TransferRoots()
    transfer = reader.WS().TransferReader()
    out = {}
    ex = TopExp_Explorer(reader.OneShape(), TopAbs_SOLID)
    while ex.More():
        shape = ex.Current()
        ex.Next()
        entity = transfer.EntityFromShapeResult(shape, 1) or transfer.EntityFromShapeResult(shape, -1)
        name = entity.Name().ToCString() if entity is not None else f"unnamed-{len(out)}"
        if names is None or name in names:
            out[name] = shape
    return out


def load_solids_at(ref, names=None):
    """The same, from the STEP as committed at git `ref` (e.g. HEAD)."""
    if not ref or ref.startswith("-"):
        raise ValueError(f"not a git ref: {ref!r}")
    with tempfile.NamedTemporaryFile(suffix=".step") as f:
        subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{STEP_PATH}"], stdout=f, check=True)
        f.flush()
        return load_solids(f.name, names)


def inlay_solids(solids, name=INLAY):
    """The STEP solids of the two-colour inlay called `name` in the 3MFs: the solid of that
    name, or for counter-face-inlay the loose bodies Body1, Body2, ..."""
    if name in solids:
        return [solids[name]]
    if name == INLAY:
        return [s for n, s in solids.items() if INLAY_BODY.fullmatch(n)]
    return []


def volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def mass_frame(shape):
    """(centre of mass, 3x3 inertia matrix about it), exact from the solid."""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    c, m = props.CentreOfMass(), props.MatrixOfInertia()
    return np.array([c.X(), c.Y(), c.Z()]), np.array([[m.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)])


def tessellate(shape, lin=0.005, ang=0.05):
    """Trimesh of a solid. `lin` is the chord error in mm, `ang` the angle limit in radians.

    OCCT's mesher leaves out or garbles some cone faces from Fusion; when the mesh does not
    close or its volume is off, the solid is converted to NURBS surfaces and meshed again.
    Callers that need a closed mesh must still check is_watertight.
    """
    m = _mesh(shape, lin, ang)
    if not m.is_watertight or abs(m.volume / volume(shape) - 1) > 0.001:
        BRepTools.Clean_s(shape)   # drop the bad mesh so the copy does not inherit it
        m = _mesh(BRepBuilderAPI_NurbsConvert(shape, True).Shape(), lin, ang)
    return m


def _mesh(shape, lin, ang):
    BRepMesh_IncrementalMesh(shape, lin, False, ang, True)
    verts, faces, off = [], [], 0
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = TopoDS.Face(ex.Current())
        ex.Next()
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is None:
            continue
        tr = loc.Transformation()
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(tr)
            verts.append((p.X(), p.Y(), p.Z()))
        reverse = face.Orientation() == TopAbs_REVERSED
        for i in range(1, tri.NbTriangles() + 1):
            a, b, c = tri.Triangle(i).Get()
            faces.append((off + a - 1, off + c - 1, off + b - 1) if reverse else (off + a - 1, off + b - 1, off + c - 1))
        off += tri.NbNodes()
    m = trimesh.Trimesh(np.array(verts), np.array(faces), process=True)
    m.merge_vertices(digits_vertex=6)
    trimesh.repair.fix_normals(m)
    return m


def tessellate_all(shapes, **kw):
    """One mesh holding several solids (e.g. the inlay bodies)."""
    return trimesh.util.concatenate([tessellate(s, **kw) for s in shapes])
