"""Give each counter option its own plate in the Bambu project, so builders print their choice
and delete nothing.

Safe to run again: a plate that exists (by name) is reused, an object already on its plate
stays where it is, and a plate whose parts are not in the project is skipped with a note.
Parts shared by every option (counter-coupling-gear, counter-gear) stay on their
small-parts plate. A new option is a new line in LAYOUT, once `add` has put its parts in
the project.

Usage: python -m cad.layout [--project FILE] [--dry-run]
"""
import argparse
import sys

from . import PROJECT, user_path
from .project import NoRoom, Project, print_plates

# (plate name, the objects on it), in the order the plates are made
LAYOUT = [
    ("Counter cover - simple (choose ONE cover)", ["simple-cover"]),
    ("Counter cover - drag (choose ONE cover)", ["drag-cover"]),
    ("Counter idlers - 25 frames (choose ONE set)", ["counter-idler-1", "counter-idler-2"]),
    ("Counter face - simple 25 (0.2 mm nozzle if possible)", ["simple-counter-face"]),
    ("Counter face - drag 25 (0.2 mm nozzle if possible)", ["drag-counter-face"]),
]


def apply(project, layout=LAYOUT):
    """Make the plates and move the objects; returns [lines saying what was done]."""
    said = []
    objects = {o["name"]: o["object_id"] for o in project.objects()}
    plates = {p["name"]: p["id"] for p in project.plates()}
    for name, parts in layout:
        present = [p for p in parts if p in objects]
        missing = [p for p in parts if p not in objects]
        if not present:
            said.append(f"skipped {name!r}: not in the project yet: {', '.join(missing)}")
            continue
        if missing:
            said.append(f"{name!r}: not in the project yet: {', '.join(missing)}")
        if name not in plates:
            plates[name] = project.add_plate(name)
            said.append(f"added plate {plates[name]}: {name}")
        for part in present:
            oid = objects[part]
            if project.plate_of(oid) == plates[name]:
                continue
            was = project.plate_of(oid)
            project.move(oid, plates[name])
            said.append(f"moved {part} from plate {was} to plate {plates[name]}")
    return said


def main(argv=None):
    ap = argparse.ArgumentParser(prog="layout", description=__doc__.splitlines()[0])
    ap.add_argument("--project", type=user_path, default=PROJECT, help="project 3MF (default: the one in 3mf/)")
    ap.add_argument("--dry-run", action="store_true", help="say what would change, write nothing")
    args = ap.parse_args(argv)

    project = Project(args.project)
    try:
        said = apply(project)
    except NoRoom as e:
        print(f"{e}\nnothing written")
        return 1
    print("\n".join(said))
    changed = any(not line.startswith("skipped") and "not in the project yet" not in line for line in said)
    problems = project.plate_problems()
    for plate, name, problem in problems:
        print(f"plate {plate}: {name}: {problem}")
    if problems:
        print("nothing written")
        return 1
    print()
    print_plates(project)
    if not changed:
        print("\nthe layout is already applied: nothing to write")
    elif args.dry_run:
        print("\ndry run: nothing written")
    else:
        project.save()
        print(f"\nwrote {args.project}\n\nnow run: mise run verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())
