"""Add a solid that is new in the STEP to the part 3MFs and the Bambu project, placed like a sibling.

The sibling is a part already in the 3MFs that the new one should print like (a new
counter face like simple-counter-face). Every mesh is written through the rigid transform
that maps the sibling's STEP solid onto the sibling's mesh, so the new part has the same
orientation and bed contact:

- 3mf/parts/<name>.3mf, in the same archive layout as the sibling's part file;
- 3mf/parts/<name>-two-colour.3mf, when the sibling has one: the face, the inlay (--inlay,
  a STEP solid; counter-face-inlay means the loose bodies Body1, Body2, ...) and the group;
- a project object cloned from the sibling's (print settings, assembly place), on the
  sibling's plate or --plate, at a free spot project.GAP mm clear of everything else.

Nothing is written unless every piece fits: the sibling's solid must fit its meshes within
TOLERANCE_RMS, the new solid must mesh closed and sit on the bed like the sibling, and
the plate must have room.

Usage: python -m cad.add <solid> --like <sibling> [--inlay SOLID] [--plate N|NAME]
                         [--step FILE] [--parts DIR] [--project FILE] [--dry-run]
"""
import argparse
import sys

from . import (PART_ENTRY, PARTS, PROJECT, REPO, STEP, TOLERANCE_RMS, TWO_COLOUR, file_stem, solid_name,
               user_path)
from . import step, threemf
from .fit import fit
from .project import NoRoom, Project, Z_TOLERANCE


class Refused(Exception):
    """The part cannot be added; the message says why."""


def rename(xml, names):
    """Model XML with object names and the title swapped ({old: new}), whole names only."""
    for old, new in names.items():
        xml = xml.replace(f'name="{old}"', f'name="{new}"')
        xml = xml.replace(f'<metadata name="Title">{old}</metadata>', f'<metadata name="Title">{new}</metadata>')
    return xml


def mesh_object(xml, name):
    """The object holding `name`'s mesh in a model: the one of that name, or the only mesh."""
    meshes = [o for o in threemf.objects(xml) if o["mesh"] is not None]
    named = [o for o in meshes if o["name"] == name]
    if named:
        return named[0]
    if len(meshes) == 1:
        return meshes[0]
    raise Refused(f"no mesh object named {name!r}")


def placed_like(sibling_mesh, sibling_frame, target, new_mesh, what):
    """`new_mesh` moved by the transform that fits the sibling's STEP mesh onto `target`."""
    T, err = fit(sibling_mesh, target, sibling_frame)
    if not err < TOLERANCE_RMS:
        raise Refused(f"{what}: the sibling's STEP solid does not fit its mesh (rms {err:.4f} mm)")
    out = new_mesh.copy()
    out.apply_transform(T)
    return T, err, out


def check_bed_contact(what, target, out):
    """The new part must rest on the same plane as the sibling."""
    dz = out.bounds[0, 2] - target.bounds[0, 2]
    if abs(dz) > Z_TOLERANCE:
        raise Refused(f"{what}: the new part's lowest point is {dz:+.4f} mm from the sibling's; "
                      "it does not share the sibling's bed contact, so place it by hand")


def plan(solid, sibling, inlay, plate, solids, parts, project):
    """({new part file path: model xml, with the sibling's file as template}, Project with the
    new object), or Refused."""
    stem, sib_stem = file_stem(solid), file_stem(sibling)
    for name in (solid, sibling):
        if name not in solids:
            raise Refused(f"no solid named {name!r} in the STEP")
    if (parts / f"{stem}.3mf").exists():
        raise Refused(f"{stem}.3mf already exists; use export to update it")
    if any(o["name"] == solid for o in project.objects()):
        raise Refused(f"the project already has an object named {solid!r}")
    sib_file = parts / f"{sib_stem}.3mf"
    if not sib_file.exists():
        raise Refused(f"the sibling has no part file {sib_file.name}")

    m_new = step.tessellate(solids[solid])
    if not (m_new.is_watertight and m_new.is_winding_consistent and m_new.volume > 0):
        raise Refused(f"{solid}: the solid does not mesh into a closed shape")
    m_sib, frame = step.tessellate(solids[sibling]), step.mass_frame(solids[sibling])
    print(f"{solid}: volume {step.volume(solids[solid]):.3f} mm3, {len(m_new.faces)} triangles, like {sibling}")
    files = {}

    # the part file
    xml = threemf.read_entry(sib_file, PART_ENTRY)
    target = mesh_object(xml, sibling)
    _, err, out = placed_like(m_sib, frame, target["mesh"], m_new, sib_file.name)
    check_bed_contact(sib_file.name, target["mesh"], out)
    files[(sib_file, parts / f"{stem}.3mf")] = rename(threemf.replace_mesh(xml, out, target["id"]),
                                                      {sibling: solid, sib_stem: stem})
    print(f"  {stem}.3mf  sibling fit rms {err:.4f} mm, lowest z {out.bounds[0, 2]:.3f}")

    # the two-colour file
    sib_two = parts / f"{sib_stem}{TWO_COLOUR}.3mf"
    if inlay is not None and not sib_two.exists():
        raise Refused(f"--inlay given, but the sibling has no {sib_two.name} to copy")
    if sib_two.exists():
        if inlay is None:
            raise Refused(f"the sibling has {sib_two.name}: give --inlay <STEP solid> for the new part's inlay")
        bodies = step.inlay_solids(solids, inlay)
        if not bodies:
            raise Refused(f"no inlay solid {inlay!r} in the STEP")
        xml = threemf.read_entry(sib_two, PART_ENTRY)
        face = mesh_object(xml, sibling)
        others = [o for o in threemf.objects(xml) if o["mesh"] is not None and o["id"] != face["id"]]
        if len(others) != 1:
            raise Refused(f"{sib_two.name}: expected one inlay object beside the face")
        T, err, out = placed_like(m_sib, frame, face["mesh"], m_new, sib_two.name)
        check_bed_contact(sib_two.name, face["mesh"], out)
        m_inlay = step.tessellate_all(bodies)
        m_inlay.apply_transform(T)
        xml = threemf.replace_mesh(threemf.replace_mesh(xml, out, face["id"]), m_inlay, others[0]["id"])
        files[(sib_two, parts / f"{stem}{TWO_COLOUR}.3mf")] = rename(
            xml, {sibling: solid, others[0]["name"]: inlay, f"{sib_stem}{TWO_COLOUR}": f"{stem}{TWO_COLOUR}"})
        print(f"  {stem}{TWO_COLOUR}.3mf  sibling fit rms {err:.4f} mm, inlay {inlay} "
              f"({len(bodies)} solid{'s' if len(bodies) > 1 else ''})")

    # the project object
    sib_obj = project.object_named(sibling)
    local = project.local_mesh(sib_obj)
    _, err, out = placed_like(m_sib, frame, local, m_new, "project")
    world_sib, world_new = local.copy(), out.copy()
    world_sib.apply_transform(sib_obj["transform"])
    world_new.apply_transform(sib_obj["transform"])
    check_bed_contact("project", world_sib, world_new)
    oid = project.clone_object(sib_obj, solid, out, f"{stem}.3mf")
    target_plate = project.plate(plate) if plate is not None else project.plate_of(sib_obj["object_id"])
    near = None
    if target_plate == project.plate_of(sib_obj["object_id"]):
        c = project.placed(sib_obj["object_id"]).centroid
        near = c.x, c.y
    try:
        project.move(oid, target_plate, near)
    except NoRoom as e:
        raise Refused(f"plate {target_plate}: {e}")
    x0, y0 = project.origin(target_plate)
    c = project.placed(oid).centroid
    print(f"  project: object {oid} on plate {target_plate} at ({c.x - x0:.1f}, {c.y - y0:.1f}) on the bed, "
          f"sibling fit rms {err:.4f} mm")
    return files, project


def main(argv=None):
    ap = argparse.ArgumentParser(prog="add", description=__doc__.splitlines()[0])
    ap.add_argument("solid", help="the new STEP solid (or its part file name)")
    ap.add_argument("--like", required=True, help="the sibling part to copy placement and settings from")
    ap.add_argument("--inlay", help="STEP solid of the two-colour inlay (counter-face-inlay: the Body1.. bodies)")
    ap.add_argument("--plate", help="project plate, by number or name (default: the sibling's)")
    ap.add_argument("--step", type=user_path, default=STEP, help="STEP to read (default: the one in cad/)")
    ap.add_argument("--parts", type=user_path, default=PARTS, help="folder of part 3MFs (default: 3mf/parts)")
    ap.add_argument("--project", type=user_path, default=PROJECT, help="project 3MF (default: the one in 3mf/)")
    ap.add_argument("--dry-run", action="store_true", help="work it all out, write nothing")
    args = ap.parse_args(argv)

    solid, sibling = solid_name(args.solid), solid_name(args.like)
    solids = step.load_solids(args.step)
    try:
        files, project = plan(solid, sibling, args.inlay, args.plate, solids, args.parts, Project(args.project))
    except Refused as e:
        print(f"{solid}: {e}\nnothing written")
        return 1
    problems = [p for p in project.plate_problems() if solid in p[1]]
    if problems:
        print("\n".join(f"plate {p}: {n}: {why}" for p, n, why in problems) + "\nnothing written")
        return 1
    if args.dry_run:
        print("\ndry run: nothing written")
        return 0
    for (template, path), xml in files.items():
        threemf.rewrite_zip(template, {PART_ENTRY: xml}, out=path)
        print(f"wrote {show(path)}")
    project.save()
    print(f"wrote {show(project.path)}\n\nnow run: mise run verify")
    return 0


def show(path):
    return path.relative_to(REPO) if path.is_relative_to(REPO) else path


if __name__ == "__main__":
    sys.exit(main())
