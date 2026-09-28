"""STEP to 3MF export and checks for the remix. Units are mm.

Run the commands from the tools folder, or through mise:
  mise run verify                 every part 3MF and project object against the STEP
  mise run export -- <names>      re-export parts from the STEP, keeping their placement
  mise run clearance              counter gears against the body, the covers and each other
  mise run add -- <solid> --like <sibling>    a new STEP solid into the 3MFs, placed like a sibling
  mise run plates -- list         plates in the project; also add-plate, rename-plate, move
  mise run layout                 one plate per counter option
"""
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STEP_PATH = "cad/Infidex176V-IDENTIDEM.design-remix.step"   # relative to REPO, as git sees it
STEP = REPO / STEP_PATH
PROJECT = REPO / "3mf" / "Infidex176V-IDENTIDEM.design-remix.3mf"
PARTS = REPO / "3mf" / "parts"
PART_ENTRY = "3D/3dmodel.model"   # the model inside every part 3MF

TOLERANCE_RMS = 0.02      # mm, surface fit between a mesh and its source
TOLERANCE_VOLUME = 0.005  # relative volume difference

# part file names whose STEP solid is named differently
FILE_TO_SOLID = {"pressure-plate-1": "pressure-plate (1)"}
TWO_COLOUR = "-two-colour"
# the two-colour inlay: one object in a two-colour 3MF, named after its STEP solid, e.g.
# counter-face-20-inlay. The 25-frame inlay is the exception: the unnamed STEP bodies
# Body1, Body2, ... that the 3MFs call counter-face-inlay.
INLAY = "counter-face-inlay"
INLAY_BODY = re.compile(r"Body\d+")
INLAY_SUFFIX = "-inlay"


def solid_name(file_stem):
    """STEP solid for a part file name (without .3mf), ignoring any two-colour suffix."""
    stem = file_stem.removesuffix(TWO_COLOUR)
    return FILE_TO_SOLID.get(stem, stem)


def file_stem(solid):
    """Part file name (without .3mf) for a STEP solid."""
    for stem, name in FILE_TO_SOLID.items():
        if name == solid:
            return stem
    return solid


def user_path(path):
    """A path given on the command line, taken from where the user ran mise (mise runs the
    tasks from tools/)."""
    return Path(os.environ.get("MISE_ORIGINAL_CWD", ".")) / path
