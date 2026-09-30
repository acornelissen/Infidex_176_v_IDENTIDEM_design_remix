"""Re-export parts from the STEP into their part 3MFs and the Bambu project, keeping placement.

Every mesh that holds a part (its part file, a two-colour file with it, its project object)
is placed on the bed in its own way. For each one, the part's solid from the STEP as
committed at --ref is fitted onto the mesh, and the solid from the current STEP is written
through the same transform. A solid whose shape is unchanged is placed by its own fit
instead, so moving it in the assembly does not move it on the bed. Everything else in each
archive is copied byte for byte.
If any old solid does not fit its mesh, nothing is written.

Export is safe to run twice before committing: a mesh that the current solid already fits
better than the old one, and within ALREADY_RMS, is reported as already exported and left
alone, so it is never refitted against the wrong solid.

Usage: python -m cad.export [--ref REF] [--step FILE] [--dry-run] <part names...>
"""
import argparse
import sys

from . import PART_ENTRY, PARTS, PROJECT, REPO, STEP, TOLERANCE_RMS, solid_name, user_path
from . import step, threemf
from .fit import fit

SETTINGS = "Metadata/model_settings.config"
ALREADY_RMS = 1e-3   # mm; the new solid fits this closely, so the mesh is already the new part


def place(m_old, m_new, target, old_frame=None, new_frame=None):
    """How to write the new solid onto `target`: (verdict, T, rms).

    - "already": the mesh already is the new solid (the new one fits within ALREADY_RMS and
      the old one does not), so it is left alone.
    - "export" through the new solid's own fit: both fit within ALREADY_RMS, so the shape is
      unchanged. The solid may have moved in the assembly; its own fit keeps it where the
      mesh is on the bed, where the old fit would carry the move along.
    - "export" through the old solid's fit otherwise: the shape changed, and the old fit
      keeps what stayed the same where it was."""
    T, err = fit(m_old, target, old_frame)
    T_new, err_new = fit(m_new, target, new_frame)
    if err_new < ALREADY_RMS:
        return ("export" if err < ALREADY_RMS else "already"), T_new, err_new
    return "export", T, err


def targets(solid):
    """[(zip path, entry, object id, project object id or None)] for every mesh of `solid`."""
    out = []
    for path in sorted(PARTS.glob("*.3mf")):
        if solid_name(path.stem) != solid:
            continue
        meshes = [o for o in threemf.objects(threemf.read_entry(path, PART_ENTRY)) if o["mesh"] is not None]
        named = [o for o in meshes if o["name"] == solid] or (meshes if len(meshes) == 1 else [])
        out += [(path, PART_ENTRY, o["id"], None) for o in named]
    for o in threemf.project_objects(PROJECT):
        if o["name"] == solid:
            out.append((PROJECT, o["mesh_file"], o["mesh_object_id"], o["object_id"]))
    return out


def plan_part(solid, old, new, plan):
    """Add the new meshes of one part to `plan` ({zip path: {entry: text}}). Returns False,
    after saying why, if the part cannot be exported."""
    if solid not in new:
        print(f"{solid}: not in the current STEP")
        return False
    if solid not in old:
        print(f"{solid}: not in the STEP at the old ref; a new part has to be added to the 3MFs by hand")
        return False
    where = targets(solid)
    if not where:
        print(f"{solid}: no part file or project object holds it")
        return False
    m_old, m_new = step.tessellate(old[solid]), step.tessellate(new[solid])
    if not (m_new.is_watertight and m_new.is_winding_consistent and m_new.volume > 0):
        print(f"{solid}: the new solid does not mesh into a closed shape")
        return False
    print(f"{solid}: volume {step.volume(old[solid]):.3f} -> {step.volume(new[solid]):.3f} mm3, "
          f"{len(m_new.faces)} triangles")
    ok = True
    for path, entry, oid, project_oid in where:
        files = plan.get(path, {})
        xml = files.get(entry) or threemf.read_entry(path, entry)
        target = next(o["mesh"] for o in threemf.objects(xml) if o["id"] == oid)
        verdict, T, err = place(m_old, m_new, target, step.mass_frame(old[solid]), step.mass_frame(new[solid]))
        if verdict == "already":
            print(f"  {path.name}:{entry}  already exported (new fit rms {err:.4f} mm), left as it is")
            continue
        out = m_new.copy()
        out.apply_transform(T)
        fits = err < TOLERANCE_RMS
        print(f"  {path.name}:{entry}  fit rms {err:.4f} mm  "
              f"lowest z {target.bounds[0, 2]:.3f} -> {out.bounds[0, 2]:.3f}  {'ok' if fits else 'NO FIT'}")
        if not fits:
            ok = False
            continue
        files = plan.setdefault(path, {})
        files[entry] = threemf.replace_mesh(xml, out, oid)
        if project_oid is not None:
            settings = files.get(SETTINGS) or threemf.read_entry(path, SETTINGS)
            files[SETTINGS] = threemf.set_face_count(settings, project_oid, len(out.faces))
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser(prog="export", description=__doc__.splitlines()[0])
    ap.add_argument("parts", nargs="+", help="part file names or STEP solid names")
    ap.add_argument("--ref", default="HEAD", help="git ref of the STEP the meshes were made from (default HEAD)")
    ap.add_argument("--step", type=user_path, default=STEP, help="STEP to export from (default: the one in cad/)")
    ap.add_argument("--dry-run", action="store_true", help="fit and report, write nothing")
    args = ap.parse_args(argv)

    solids = {solid_name(p) for p in args.parts}
    old = step.load_solids_at(args.ref, solids)
    new = step.load_solids(args.step, solids)
    plan = {}
    ok = all([plan_part(s, old, new, plan) for s in sorted(solids)])
    if not ok:
        print(f"\nnothing written: the old STEP must fit every mesh within {TOLERANCE_RMS} mm")
        return 1
    if not plan:
        print("\nnothing to write: every mesh is already exported")
        return 0
    if args.dry_run:
        print("\ndry run: nothing written")
        return 0
    for path, files in plan.items():
        threemf.rewrite_zip(path, files)
        print(f"wrote {path.relative_to(REPO)}: {', '.join(sorted(files))}")
    print("\nnow run: mise run verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
