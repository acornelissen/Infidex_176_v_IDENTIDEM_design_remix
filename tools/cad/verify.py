"""Check every part 3MF, and every object in the Bambu project, against the STEP.

For each mesh: watertight, consistent winding, positive volume. A part file must match
the STEP solid of the same name (fit RMS and volume); a two-colour file holds the face
and the inlay, and the inlay must sit where the STEP puts it relative to the face. Every
project object must match the mesh in its part file.

Usage: python -m cad.verify [--step FILE] [part names...]    (all parts when none are given)
Exits 1 if anything fails.
"""
import argparse
import sys

from . import (INLAY, INLAY_BODY, PART_ENTRY, PARTS, PROJECT, STEP, TOLERANCE_RMS, TOLERANCE_VOLUME, TWO_COLOUR,
               file_stem, solid_name, user_path)
from . import step, threemf
from .fit import fit, vertex_rms


def mesh_problems(mesh):
    out = []
    if not mesh.is_watertight:
        out.append("not watertight")
    if not mesh.is_winding_consistent:
        out.append("inconsistent winding")
    if not mesh.volume > 0:
        out.append("volume not positive")
    return out


def row(file, obj, mesh, ref_volume=None, rms=None, problems=()):
    """One table row; adds the fit and volume verdicts to the mesh's own problems."""
    problems = mesh_problems(mesh) + list(problems)
    dv = None
    if ref_volume:
        dv = (mesh.volume - ref_volume) / ref_volume
        if abs(dv) > TOLERANCE_VOLUME:
            problems.append(f"volume off by {dv:+.2%}")
    if rms is not None and not rms < TOLERANCE_RMS:
        problems.append(f"fit rms {rms:.4f} mm")
    return {"file": file, "object": obj, "rms": rms, "volume": mesh.volume, "ref_volume": ref_volume,
            "dv": dv, "problems": problems}


def check_part_file(path, solids, step_mesh):
    """Rows for one part 3MF against the STEP."""
    meshes = threemf.mesh_objects(threemf.read_entry(path, PART_ENTRY))
    face = solid_name(path.stem)
    expected = [face, INLAY] if path.stem.endswith(TWO_COLOUR) else [face]
    if len(meshes) == 1 and len(expected) == 1:
        meshes = {face: next(iter(meshes.values()))}   # a lone mesh may carry any object name
    rows = []
    for extra in sorted(set(meshes) - set(expected)):
        rows.append(row(path.name, extra, meshes[extra], problems=["unexpected object"]))
    T = None
    for name in expected:
        if name not in meshes:
            rows.append({"file": path.name, "object": name, "rms": None, "volume": None, "ref_volume": None,
                         "dv": None, "problems": ["object missing from the file"]})
            continue
        mesh = meshes[name]
        if name == INLAY:
            bodies = step.inlay_solids(solids)
            if not bodies or T is None:
                rows.append(row(path.name, name, mesh, problems=["no inlay bodies or no face fit to place them"]))
                continue
            ref_volume = sum(step.volume(s) for s in bodies)
            rms = vertex_rms(step_mesh(INLAY), mesh, T)
            rows.append(row(path.name, name, mesh, ref_volume, rms))
        elif name not in solids:
            rows.append(row(path.name, name, mesh, problems=[f"no STEP solid named {name!r}"]))
        else:
            T, rms = fit(step_mesh(name), mesh, step.mass_frame(solids[name]))
            rows.append(row(path.name, name, mesh, step.volume(solids[name]), rms))
    return rows, meshes


def check_project(part_meshes, only):
    """Rows for every project object against the mesh in its part file."""
    rows = []
    for o in threemf.project_objects(PROJECT):
        name = o["name"]
        if only and name not in only and file_stem(name) not in only:
            continue
        label = f"project:{o['mesh_file'].rsplit('/', 1)[-1]}"
        xml = threemf.read_entry(PROJECT, o["mesh_file"])
        mesh = next(x["mesh"] for x in threemf.objects(xml) if x["id"] == o["mesh_object_id"])
        ref = part_meshes.get((file_stem(name), name))
        if ref is None:
            rows.append(row(label, name, mesh, problems=[f"no part file {file_stem(name)}.3mf holding {name!r}"]))
            continue
        _, rms = fit(ref, mesh)
        rows.append(row(label, name, mesh, ref.volume, rms))
    return rows


def print_table(rows):
    print(f"{'file':42s} {'object':34s} {'rms mm':>7s} {'volume':>10s} {'ref vol':>10s} {'dV %':>7s}  result")
    for r in rows:
        num = lambda v, f: format(v, f) if v is not None else "-"
        dv = num(r["dv"] * 100 if r["dv"] is not None else None, "+.3f")
        verdict = "ok" if not r["problems"] else "FAIL " + "; ".join(r["problems"])
        print(f"{r['file']:42s} {r['object']:34s} {num(r['rms'], '.4f'):>7s} {num(r['volume'], '.2f'):>10s} "
              f"{num(r['ref_volume'], '.2f'):>10s} {dv:>7s}  {verdict}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="verify", description=__doc__.splitlines()[0])
    ap.add_argument("parts", nargs="*", help="part file names or STEP solid names (default: all)")
    ap.add_argument("--step", type=user_path, default=STEP, help="STEP file to check against (default: the one in cad/)")
    args = ap.parse_args(argv)
    only = set(args.parts)

    solids = step.load_solids(args.step)
    cache = {}

    def step_mesh(name):
        if name not in cache:
            cache[name] = (step.tessellate_all(step.inlay_solids(solids)) if name == INLAY
                           else step.tessellate(solids[name]))
        return cache[name]

    rows, part_meshes = [], {}
    paths = sorted(PARTS.glob("*.3mf"))
    for path in paths:
        if only and path.stem not in only and solid_name(path.stem) not in only:
            continue
        r, meshes = check_part_file(path, solids, step_mesh)
        rows += r
        part_meshes.update({(path.stem, n): m for n, m in meshes.items()})
    rows += check_project(part_meshes, only)
    print_table(rows)

    if not only:
        covered = {solid_name(p.stem) for p in paths}
        loose = sorted(n for n in solids if n not in covered and not INLAY_BODY.fullmatch(n))
        if loose:
            print(f"\nnote: STEP solids with no part file: {', '.join(loose)}")
    failed = [r for r in rows if r["problems"]]
    print(f"\n{len(rows) - len(failed)} of {len(rows)} checks passed")
    return 1 if failed or not rows else 0


if __name__ == "__main__":
    sys.exit(main())
