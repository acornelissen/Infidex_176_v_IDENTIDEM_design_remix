import numpy as np
import trimesh

from cad.export import place
from test_cad_fit import known_pose, lumpy_part, moved


def old_and_new():
    """A part and its next revision: the same, with the top raised by 0.3 mm."""
    old = lumpy_part()
    new = old.copy()
    new.vertices[new.vertices[:, 2] > new.center_mass[2] + 2] += [0, 0, 0.3]
    return old, new


def test_a_mesh_of_the_old_part_is_exported_through_the_old_fit():
    old, new = old_and_new()
    T = known_pose()
    verdict, found, err = place(old, new, moved(old.subdivide(), T))
    assert verdict == "export"
    assert err < 1e-3
    np.testing.assert_allclose(trimesh.transform_points(new.vertices, found),
                               trimesh.transform_points(new.vertices, T), atol=1e-3)


def test_a_mesh_that_already_is_the_new_part_is_left_alone():
    # export already ran and wrote the new solid; the old solid only roughly fits it
    old, new = old_and_new()
    verdict, _, err = place(old, new, moved(new, known_pose()))
    assert verdict == "already"
    assert err < 1e-3


def test_an_unchanged_part_is_still_exported():
    old = lumpy_part()
    verdict, _, _ = place(old, old.copy(), moved(old, known_pose()))
    assert verdict == "export"
