"""Read and write meshes in 3MF model XML, and rewrite 3MF archives.

The 3MFs are edited as text, not re-serialised, so everything we do not touch stays
byte for byte as Bambu Studio or the exporter wrote it.
"""
import os
import re
import zipfile

import numpy as np
import trimesh

VERTEX = re.compile(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"')
TRIANGLE = re.compile(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"')
OBJECT = re.compile(r"<object\b([^>]*)>(.*?)</object>", re.S)
VERTICES = re.compile(r"(<vertices>)(.*?)(\n[ \t]*</vertices>)", re.S)
TRIANGLES = re.compile(r"(<triangles>)(.*?)(\n[ \t]*</triangles>)", re.S)


def attr(tag, key):
    """Value of attribute `key` in the text of an XML start tag, or None."""
    m = re.search(rf'(?:^|\s){re.escape(key)}="([^"]*)"', tag)
    return m.group(1) if m else None


def read_mesh(xml):
    """Mesh from the first <mesh> in `xml` (a whole model or one object's text)."""
    v = np.array(VERTEX.findall(xml), float).reshape(-1, 3)
    t = np.array(TRIANGLE.findall(xml), int).reshape(-1, 3)
    return trimesh.Trimesh(v, t, process=False)


def objects(xml):
    """[{id, name, mesh or None, components: [object ids]}] for every <object> in a model."""
    out = []
    for tag, body in OBJECT.findall(xml):
        comps = [attr(c, "objectid") for c in re.findall(r"<component\b([^>]*)/>", body)]
        out.append({"id": attr(tag, "id"), "name": attr(tag, "name"),
                    "mesh": read_mesh(body) if "<mesh>" in body else None, "components": comps})
    return out


def mesh_objects(xml):
    """{object name: mesh} for the objects in a model that hold a mesh."""
    return {o["name"]: o["mesh"] for o in objects(xml) if o["mesh"] is not None}


def mesh_lines(mesh, indent):
    """Vertex and triangle lines for `mesh`, one element per line."""
    vs = "".join(f'\n{indent}<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in mesh.vertices)
    ts = "".join(f'\n{indent}<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in mesh.faces)
    return vs, ts


def replace_mesh(xml, mesh, object_id=None):
    """`xml` with the mesh of object `object_id` (default: the first mesh) swapped for `mesh`."""
    for m in OBJECT.finditer(xml):
        if "<mesh>" in m.group(2) and (object_id is None or attr(m.group(1), "id") == str(object_id)):
            break
    else:
        raise KeyError(f"no mesh object {object_id} in the model")
    body = m.group(2)
    indent = re.search(r"\n([ \t]*)<vertex ", body).group(1)
    vs, ts = mesh_lines(mesh, indent)
    body = VERTICES.sub(lambda mo: mo.group(1) + vs + mo.group(3), body, count=1)
    body = TRIANGLES.sub(lambda mo: mo.group(1) + ts + mo.group(3), body, count=1)
    return xml[:m.start(2)] + body + xml[m.end(2):]


def read_entry(path, entry):
    with zipfile.ZipFile(path) as z:
        return z.read(entry).decode("utf-8")


def rewrite_zip(path, replacements):
    """Replace entries of the zip at `path` ({entry: str or bytes}); every other entry,
    the entry order and the per-entry compression stay as they were."""
    tmp = f"{path}.tmp"
    with zipfile.ZipFile(path) as zin:
        missing = set(replacements) - set(zin.namelist())
        if missing:
            raise KeyError(f"not in {path}: {sorted(missing)}")
        with zipfile.ZipFile(tmp, "w") as zout:
            for info in zin.infolist():
                data = replacements.get(info.filename)
                if data is None:
                    data = zin.read(info.filename)
                elif isinstance(data, str):
                    data = data.encode("utf-8")
                zout.writestr(info, data, compress_type=info.compress_type)
    os.replace(tmp, path)


def transform(text):
    """4x4 matrix from a 3MF transform attribute (row-vector order, 12 numbers)."""
    T = np.eye(4)
    if text:
        a = np.array(text.split(), float)
        T[:3, :3] = a[:9].reshape(3, 3).T
        T[:3, 3] = a[9:]
    return T


def project_objects(path):
    """The objects of a Bambu project, one dict each:
    name, object_id, mesh_file (zip entry), mesh_object_id (object inside that file),
    transform (4x4, object mesh to bed), plate (number, or None).

    Names come from Metadata/model_settings.config; each object is expected to have one
    component that points at its own mesh file, which is how Bambu Studio saves them.
    """
    with zipfile.ZipFile(path) as z:
        model = z.read("3D/3dmodel.model").decode("utf-8")
        settings = z.read("Metadata/model_settings.config").decode("utf-8")
    names = dict(re.findall(r'<object id="(\d+)">\s*<metadata key="name" value="([^"]*)"', settings))
    plates = {}
    for plate, body in re.findall(r'<plate>\s*<metadata key="plater_id" value="(\d+)"/>(.*?)</plate>', settings, re.S):
        for oid in re.findall(r'<metadata key="object_id" value="(\d+)"/>', body):
            plates[oid] = int(plate)
    items = {attr(tag, "objectid"): transform(attr(tag, "transform")) for tag in re.findall(r"<item\b([^>]*)/>", model)}
    out = []
    for tag, body in OBJECT.findall(model):
        oid = attr(tag, "id")
        comps = re.findall(r"<component\b([^>]*)/>", body)
        if len(comps) != 1 or not attr(comps[0], "p:path"):
            raise ValueError(f"project object {oid} is not a single component in its own file")
        c = comps[0]
        out.append({"name": names.get(oid), "object_id": oid,
                    "mesh_file": attr(c, "p:path").lstrip("/"), "mesh_object_id": attr(c, "objectid"),
                    "transform": items.get(oid, np.eye(4)) @ transform(attr(c, "transform")),
                    "plate": plates.get(oid)})
    return out


def set_face_count(settings, object_id, count):
    """model_settings.config text with the face counts of project object `object_id` updated."""
    m = re.search(rf'\n  <object id="{object_id}">.*?\n  </object>', settings, re.S)
    if m is None:
        raise KeyError(f"no object {object_id} in model_settings.config")
    block = re.sub(r'face_count="\d+"', f'face_count="{count}"', m.group(0))
    return settings[:m.start()] + block + settings[m.end():]
