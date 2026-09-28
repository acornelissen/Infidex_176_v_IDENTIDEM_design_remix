"""Edit the Bambu Studio project: its objects, its plates and where objects sit on them.

Bambu Studio lays the plates out in a grid, plate n (from 1) at column (n-1) % cols and
row (n-1) // cols, with its bed corner at (col * stride_x, -row * stride_y), the stride
being the bed size plus a fifth. The column count follows the plate count
(compute_colum_count in BambuStudio src/slic3r/GUI/PartPlate.hpp): the square root,
rounded, plus one if the root is above its rounding. On loading, Bambu Studio gives each
object to the plate it sits on, so when adding a plate changes the column count every
object is moved by the shift of its plate's corner.

Everything is edited as text, as in threemf, so what is not touched stays as it was.

Usage: python -m cad.project list
       python -m cad.project add-plate <name>
       python -m cad.project rename-plate <plate> <name>
       python -m cad.project move <object name> <plate>
A plate is given by number or by name.
"""
import argparse
import json
import math
import re
import sys
import zipfile
from xml.sax.saxutils import escape, unescape

import numpy as np
from shapely import affinity, prepared
from shapely.geometry import MultiPoint, Polygon, box
from shapely.ops import unary_union

from . import PROJECT, REPO, user_path
from . import threemf

MODEL = "3D/3dmodel.model"
RELS = "3D/_rels/3dmodel.model.rels"
SETTINGS = "Metadata/model_settings.config"
CUT = "Metadata/cut_information.xml"
SEQUENCE = "Metadata/filament_sequence.json"
PRINTER = "Metadata/project_settings.config"

PLATE_GAP = 0.2       # LOGICAL_PART_PLATE_GAP: the space between plates, as a share of the bed
GAP = 6.0             # mm, least distance between two objects on a plate
EDGE = 3.0            # mm, least distance from a placed object to the edge of the bed
Z_TOLERANCE = 1e-3    # mm, how far off the bed the lowest point of an object may be
GRID = 1.0            # mm, step of the search for a free spot

ATTR_ESCAPES = {'"': "&quot;"}


class NoRoom(Exception):
    """No free spot on the plate."""


def columns(count):
    """Plate columns Bambu Studio uses for `count` plates (compute_colum_count)."""
    value = math.sqrt(count)
    rounded = round(value)
    return rounded + 1 if value > rounded else rounded


def plate_origin(plate, cols, width, depth):
    """(x, y) of the bed corner of plate `plate` (from 1) in a grid of `cols` columns."""
    row, col = divmod(plate - 1, cols)
    return col * width * (1 + PLATE_GAP), -row * depth * (1 + PLATE_GAP)


def number(v):
    """A coordinate as the 3MFs write them: short, no trailing zeros."""
    text = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def footprint(mesh):
    """Outline of a mesh on the bed: the convex hull of its vertices seen from above."""
    return MultiPoint(mesh.vertices[:, :2]).convex_hull


def free_spot(shape, bed, blocked, near, grid=GRID):
    """Offset (dx, dy) that puts `shape` inside `bed` clear of every polygon in `blocked`,
    with its centre as near `near` as the grid allows. Raises NoRoom."""
    minx, miny, maxx, maxy = shape.bounds
    bminx, bminy, bmaxx, bmaxy = bed.bounds
    xs = np.arange(bminx - minx, bmaxx - maxx + 1e-9, grid)
    ys = np.arange(bminy - miny, bmaxy - maxy + 1e-9, grid)
    if not len(xs) or not len(ys):
        raise NoRoom("the part is larger than the bed")
    cx, cy = shape.centroid.x, shape.centroid.y
    gx, gy = np.meshgrid(xs, ys)
    order = np.argsort((gx + cx - near[0]) ** 2 + (gy + cy - near[1]) ** 2, axis=None)
    inside = prepared.prep(bed)
    taken = prepared.prep(unary_union(blocked)) if blocked else None
    for i in order:
        dx, dy = gx.flat[i], gy.flat[i]
        moved = affinity.translate(shape, dx, dy)
        if inside.contains(moved) and (taken is None or not taken.intersects(moved)):
            return float(dx), float(dy)
    raise NoRoom("no free spot on the plate")


def plate_blocks(settings):
    """[(match start, match end, plate number, name, [object ids])] for every <plate>."""
    out = []
    for m in re.finditer(r"\n  <plate>\n.*?\n  </plate>", settings, re.S):
        body = m.group(0)
        pid = int(re.search(r'key="plater_id" value="(\d+)"', body).group(1))
        name = re.search(r'key="plater_name" value="([^"]*)"', body)
        oids = re.findall(r'<metadata key="object_id" value="(\d+)"/>', body)
        out.append((m.start(), m.end(), pid, unescape(name.group(1), {"&quot;": '"'}) if name else "", oids))
    return out


def plate_block(pid, name, filament_map_mode):
    """A new, empty <plate> block. The thumbnail keys are left out: Bambu Studio draws the
    thumbnails again when it saves."""
    return (f'\n  <plate>\n    <metadata key="plater_id" value="{pid}"/>\n'
            f'    <metadata key="plater_name" value="{escape(name, ATTR_ESCAPES)}"/>\n'
            f'    <metadata key="locked" value="false"/>\n'
            f'    <metadata key="filament_map_mode" value="{filament_map_mode}"/>\n  </plate>')


def instance_block(oid, identify_id):
    return (f'    <model_instance>\n      <metadata key="object_id" value="{oid}"/>\n'
            f'      <metadata key="instance_id" value="0"/>\n'
            f'      <metadata key="identify_id" value="{identify_id}"/>\n    </model_instance>\n')


def settings_object_block(settings, oid):
    """The <object id="oid"> block of model_settings.config, with its line ending."""
    m = re.search(rf'  <object id="{oid}">\n.*?\n  </object>\n', settings, re.S)
    if m is None:
        raise KeyError(f"no object {oid} in model_settings.config")
    return m.group(0)


def clone_settings_object(settings, sibling, oid, name, face_count, source_file, uuid):
    """model_settings.config with a copy of object `sibling`'s block, as object `oid` named
    `name`, placed after the sibling. Print settings (infill, walls, extruder) carry over;
    the part gets id oid - 1, a new uuid, the face count and a source file of its own."""
    block = settings_object_block(settings, sibling)
    new = block.replace(f'<object id="{sibling}">', f'<object id="{oid}">', 1)
    new = re.sub(r'(<metadata key="name" value=")[^"]*(")', rf"\g<1>{escape(name, ATTR_ESCAPES)}\g<2>", new)
    new = re.sub(r'<part id="\d+"', f'<part id="{int(oid) - 1}"', new)
    new = re.sub(r'uuid="[^"]*"', f'uuid="{uuid}"', new)
    new = re.sub(r'face_count="\d+"', f'face_count="{face_count}"', new)
    new = re.sub(r'(<metadata key="source_file" value=")[^"]*"', rf'\g<1>{escape(source_file, ATTR_ESCAPES)}"', new)
    new = re.sub(r'(<metadata key="source_(?:object_id|volume_id|offset_[xyz])" value=")[^"]*"', r'\g<1>0"', new)
    at = settings.index(block) + len(block)
    settings = settings[:at] + new + settings[at:]
    # the assembly view: same place as the sibling
    lines = re.findall(rf'   <assemble_item object_id="{sibling}"[^\n]*\n', settings)
    copies = "".join(line.replace(f'object_id="{sibling}"', f'object_id="{oid}"', 1) for line in lines)
    return settings.replace("  </assemble>", copies + "  </assemble>", 1)


class Project:
    """A Bambu Studio project opened for editing. Nothing is written until save()."""

    def __init__(self, path=PROJECT):
        self.path = path
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            self.text = {e: z.read(e).decode("utf-8") for e in (MODEL, RELS, SETTINGS, CUT, SEQUENCE) if e in names}
            printer = json.loads(z.read(PRINTER)) if PRINTER in names else {}
        self.entries = names
        self.added = {}              # new zip entries: {name: text}
        corners = np.array([[float(v) for v in c.split("x")] for c in printer.get("printable_area", ["0x0", "256x256"])])
        self.width, self.depth = (corners.max(0) - corners.min(0)).tolist()
        area = printer.get("bed_exclude_area") or []
        self.exclude = Polygon([[float(v) for v in c.split("x")] for c in area]) if len(area) >= 3 else None
        self._shapes = {}            # object id: (footprint at zero translation, lowest z)

    # ------------------------------------------------------------------ reading
    def read(self, entry):
        if entry in self.added:
            return self.added[entry]
        if entry in self.text:
            return self.text[entry]
        with zipfile.ZipFile(self.path) as z:
            return z.read(entry).decode("utf-8")

    def objects(self):
        return threemf.parse_project(self.text[MODEL], self.text[SETTINGS])

    def object_named(self, name):
        found = [o for o in self.objects() if o["name"] == name]
        if len(found) != 1:
            raise KeyError(f"{len(found)} project objects named {name!r}")
        return found[0]

    def plates(self):
        """[{id, name, objects: [object ids]}], in plate order."""
        return [{"id": pid, "name": name, "objects": oids} for _, _, pid, name, oids in plate_blocks(self.text[SETTINGS])]

    def plate(self, key):
        """Plate number for a number or a name."""
        plates = self.plates()
        for p in plates:
            if str(p["id"]) == str(key) or p["name"] == key:
                return p["id"]
        raise KeyError(f"no plate {key!r}; plates are: " + "; ".join(f"{p['id']} {p['name']}" for p in plates))

    def plate_of(self, oid):
        return next((p["id"] for p in self.plates() if str(oid) in p["objects"]), None)

    def cols(self):
        return columns(len(self.plates()))

    def origin(self, plate, cols=None):
        return plate_origin(plate, cols or self.cols(), self.width, self.depth)

    def bed(self, plate):
        x0, y0 = self.origin(plate)
        return box(x0, y0, x0 + self.width, y0 + self.depth)

    def exclusion(self, plate):
        return None if self.exclude is None else affinity.translate(self.exclude, *self.origin(plate))

    def _item(self, oid):
        m = re.search(rf'<item objectid="{oid}"[^>]*/>', self.text[MODEL])
        if m is None:
            raise KeyError(f"no build item for object {oid}")
        return m

    def translation(self, oid):
        return threemf.transform(threemf.attr(self._item(oid).group(0), "transform"))[:3, 3]

    def local_mesh(self, o):
        """The mesh of project object `o` in its own file's coordinates."""
        xml = self.read(o["mesh_file"])
        return next(x["mesh"] for x in threemf.objects(xml) if x["id"] == o["mesh_object_id"])

    def world_mesh(self, o):
        mesh = self.local_mesh(o)
        mesh.apply_transform(o["transform"])
        return mesh

    def shape(self, oid):
        """(footprint with the object's translation taken out, lowest z)."""
        if oid not in self._shapes:
            o = next(x for x in self.objects() if x["object_id"] == oid)
            mesh = self.world_mesh(o)
            t = self.translation(oid)
            self._shapes[oid] = affinity.translate(footprint(mesh), -t[0], -t[1]), float(mesh.bounds[0, 2])
        return self._shapes[oid]

    def placed(self, oid):
        """Footprint of object `oid` where it sits now."""
        t = self.translation(oid)
        return affinity.translate(self.shape(oid)[0], t[0], t[1])

    # ------------------------------------------------------------------ writing
    def set_translation(self, oid, xyz):
        m = self._item(oid)
        tag = m.group(0)
        values = threemf.attr(tag, "transform").split()
        values[9:12] = [number(v) for v in xyz]
        new = tag.replace(f'transform="{threemf.attr(tag, "transform")}"', f'transform="{" ".join(values)}"', 1)
        self.text[MODEL] = self.text[MODEL][:m.start()] + new + self.text[MODEL][m.end():]

    def shift(self, oid, dx, dy):
        t = self.translation(oid)
        self.set_translation(oid, (t[0] + dx, t[1] + dy, t[2]))

    def _relayout(self, old_cols, new_cols):
        """Move every object by the shift of its plate's corner between two column counts."""
        if old_cols == new_cols:
            return
        for p in self.plates():
            ox, oy = plate_origin(p["id"], old_cols, self.width, self.depth)
            nx, ny = plate_origin(p["id"], new_cols, self.width, self.depth)
            for oid in p["objects"]:
                self.shift(oid, nx - ox, ny - oy)

    def add_plate(self, name):
        """Append an empty plate named `name`; returns its number."""
        blocks = plate_blocks(self.text[SETTINGS])
        if any(b[3] == name for b in blocks):
            raise ValueError(f"there is already a plate named {name!r}")
        old_cols = columns(len(blocks))
        pid = len(blocks) + 1
        mode = re.search(r'key="filament_map_mode" value="([^"]*)"', self.text[SETTINGS])
        at = blocks[-1][1]
        s = self.text[SETTINGS]
        self.text[SETTINGS] = s[:at] + plate_block(pid, name, mode.group(1) if mode else "Auto For Flush") + s[at:]
        if SEQUENCE in self.text:
            seq = json.loads(self.text[SEQUENCE])
            seq.setdefault(f"plate_{pid}", {"nozzle_sequence": [], "optimal_assignment": [], "sequence": []})
            self.text[SEQUENCE] = json.dumps(seq, separators=(",", ":"))
        self._relayout(old_cols, columns(pid))
        return pid

    def rename_plate(self, plate, name):
        pid = self.plate(plate)
        for start, end, p, _, _ in plate_blocks(self.text[SETTINGS]):
            if p == pid:
                s = self.text[SETTINGS]
                block = re.sub(r'(key="plater_name" value=")[^"]*(")', lambda m: m.group(1) + escape(name, ATTR_ESCAPES) + m.group(2),
                               s[start:end], count=1)
                self.text[SETTINGS] = s[:start] + block + s[end:]

    def free_spot(self, oid, plate, near=None):
        """Translation (x, y) that puts object `oid` on `plate` clear of the others."""
        shape, _ = self.shape(oid)
        bed = self.bed(plate)
        others = [self.placed(o).buffer(GAP) for o in self.plates()[plate - 1]["objects"] if o != oid]
        excl = self.exclusion(plate)
        if excl is not None:
            others.append(excl.buffer(EDGE))
        if near is None:
            near = bed.centroid.x, bed.centroid.y
        return free_spot(shape, bed.buffer(-EDGE, join_style="mitre"), others, near)

    def move(self, oid, plate, near=None):
        """Put object `oid` on `plate` (a number or a name) at a free spot. Raises NoRoom."""
        pid = self.plate(plate)
        dx, dy = self.free_spot(oid, pid, near)
        t = self.translation(oid)
        self.set_translation(oid, (dx, dy, t[2]))
        s = self.text[SETTINGS]
        m = re.search(rf'    <model_instance>\n      <metadata key="object_id" value="{oid}"/>\n.*?    </model_instance>\n', s, re.S)
        if m is None:
            identify = max((int(i) for i in re.findall(r'key="identify_id" value="(\d+)"', s)), default=0) + 11
            instance = instance_block(oid, identify)
        else:
            instance = m.group(0)
            s = s[:m.start()] + s[m.end():]
        end = next(e for _, e, p, _, _ in plate_blocks(s) if p == pid)
        close = s.rindex("  </plate>", 0, end)
        self.text[SETTINGS] = s[:close] + instance + s[close:]
        return pid

    def clone_object(self, sibling, name, local_mesh, source_file):
        """Add object `name` with mesh `local_mesh` (in the sibling's object-file frame), cloned
        from project object `sibling` (a project_objects dict): its object file, resource,
        build item (the sibling's transform), relationship, settings, plate and assembly place,
        and cut information. Returns the new object id; move() it to a free spot next."""
        model = self.text[MODEL]
        ids = [int(i) for i in re.findall(r'<object id="(\d+)"', model)]
        oid = max(ids) + 2
        mesh_id = oid - 1
        files = [int(n) for n in re.findall(r"3D/Objects/object_(\d+)\.model", " ".join(self.entries | set(self.added)))]
        fidx = max(files, default=0) + 1
        entry = f"3D/Objects/object_{fidx}.model"
        if name in {o["name"] for o in self.objects()}:
            raise ValueError(f"the project already has an object named {name!r}")

        xml = threemf.replace_mesh(self.read(sibling["mesh_file"]), local_mesh, sibling["mesh_object_id"])
        xml = re.sub(rf'<object id="{sibling["mesh_object_id"]}"( p:UUID="[^"]*")?',
                     f'<object id="{mesh_id}" p:UUID="{fidx:04x}0000-81cb-4c03-9d28-80fed5dfa1dc"', xml, count=1)
        self.added[entry] = xml

        resource = re.search(rf'  <object id="{sibling["object_id"]}"[^>]*>\n.*?\n  </object>\n', model, re.S).group(0)
        resource = re.sub(r'<object id="\d+" p:UUID="[^"]*"', f'<object id="{oid}" p:UUID="{fidx:08x}-61cb-4c03-9d28-80fed5dfa1dc"', resource, count=1)
        resource = re.sub(r'p:path="[^"]*" objectid="\d+" p:UUID="[^"]*"',
                          f'p:path="/{entry}" objectid="{mesh_id}" p:UUID="{fidx:04x}0000-b206-40ff-9872-83e8017abed1"', resource, count=1)
        model = model.replace(" </resources>", resource + " </resources>", 1)
        item = self._item(sibling["object_id"]).group(0)
        item = re.sub(r'objectid="\d+"', f'objectid="{oid}"', item, count=1)
        item = re.sub(r'p:UUID="[^"]*"', f'p:UUID="{oid:08x}-b1ec-4553-aec9-835e5b724bb4"', item, count=1)
        self.text[MODEL] = re.sub(r"(\n)( </build>)", lambda m: f"\n  {item}\n" + m.group(2), model, count=1)

        rels = self.text[RELS]
        n = max((int(i) for i in re.findall(r'Id="rel-(\d+)"', rels)), default=0) + 1
        self.text[RELS] = rels.replace("</Relationships>", f' <Relationship Target="/{entry}" Id="rel-{n}" '
                                       'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>', 1)

        uuid = f"{fidx:04x}0000-6a6a-4d2e-9d5b-{oid:012x}"
        self.text[SETTINGS] = clone_settings_object(self.text[SETTINGS], sibling["object_id"], oid, name,
                                                    len(local_mesh.faces), source_file, uuid)
        plate = self.plate_of(sibling["object_id"])
        s = self.text[SETTINGS]
        identify = max(int(i) for i in re.findall(r'key="identify_id" value="(\d+)"', s)) + 11
        end = next(e for _, e, p, _, _ in plate_blocks(s) if p == plate)
        close = s.rindex("  </plate>", 0, end)
        self.text[SETTINGS] = s[:close] + instance_block(oid, identify) + s[close:]

        if CUT in self.text:
            cut = self.text[CUT]
            n = max((int(i) for i in re.findall(r'<object id="(\d+)"', cut)), default=0) + 1
            self.text[CUT] = cut.replace("</objects>", f' <object id="{n}">\n  <cut_id id="0" check_sum="1" connectors_cnt="0"/>\n'
                                         " </object>\n</objects>", 1)
        return str(oid)

    def save(self, out=None):
        changed = {e: t for e, t in self.text.items()}
        threemf.rewrite_zip(self.path, changed, self.added, before=SETTINGS if self.added else None, out=out)

    # ------------------------------------------------------------------ checks
    def plate_problems(self):
        """[(plate, object name, problem)] for objects off their bed, in the excluded corner,
        not on the bed surface, or closer than GAP to another object on the plate."""
        out = []
        names = {o["object_id"]: o["name"] for o in self.objects()}
        for p in self.plates():
            bed, excl = self.bed(p["id"]), self.exclusion(p["id"])
            shapes = {}
            for oid in p["objects"]:
                name = names.get(oid, oid)
                shapes[oid] = fp = self.placed(oid)
                zmin = self.shape(oid)[1]
                if not bed.buffer(1e-3).contains(fp):
                    out.append((p["id"], name, "off the bed"))
                if excl is not None and fp.intersects(excl):
                    out.append((p["id"], name, "in the bed's excluded area"))
                if abs(zmin) > Z_TOLERANCE:
                    out.append((p["id"], name, f"lowest point at z {zmin:.4f}, not on the bed"))
            oids = list(shapes)
            for i, a in enumerate(oids):
                for b in oids[i + 1:]:
                    d = shapes[a].distance(shapes[b])
                    if d < GAP - 1e-6:
                        out.append((p["id"], f"{names.get(a, a)} / {names.get(b, b)}", f"only {d:.2f} mm apart"))
        return out


def print_plates(project):
    names = {o["object_id"]: o["name"] for o in project.objects()}
    print(f"{len(project.plates())} plates, {project.cols()} columns")
    for p in project.plates():
        print(f"{p['id']:3d}  {p['name']}")
        for oid in p["objects"]:
            print(f"       {names.get(oid, oid)}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="plates", description=__doc__.splitlines()[0])
    ap.add_argument("--project", type=user_path, default=PROJECT, help="project 3MF (default: the one in 3mf/)")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list the plates and their objects")
    a = sub.add_parser("add-plate", help="append an empty plate")
    a.add_argument("name")
    r = sub.add_parser("rename-plate", help="rename a plate")
    r.add_argument("plate")
    r.add_argument("name")
    m = sub.add_parser("move", help="move an object to a free spot on a plate")
    m.add_argument("object")
    m.add_argument("plate")
    args = ap.parse_args(argv)

    project = Project(args.project)
    if args.command == "list":
        print_plates(project)
        return 0
    if args.command == "add-plate":
        print(f"added plate {project.add_plate(args.name)}: {args.name}")
    elif args.command == "rename-plate":
        project.rename_plate(args.plate, args.name)
    elif args.command == "move":
        try:
            pid = project.move(project.object_named(args.object)["object_id"], args.plate)
        except NoRoom as e:
            print(f"{args.object}: {e}")
            return 1
        print(f"moved {args.object} to plate {pid}")
    problems = project.plate_problems()
    for plate, name, problem in problems:
        print(f"plate {plate}: {name}: {problem}")
    project.save()
    print(f"wrote {project.path.relative_to(REPO) if project.path.is_relative_to(REPO) else project.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
