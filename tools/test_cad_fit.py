import numpy as np
import trimesh

from cad import FILE_TO_SOLID, file_stem, solid_name
from cad.fit import fit, match_vertices


def lumpy_part():
    """A closed mesh with no symmetry, so there is only one right answer."""
    points = np.random.default_rng(7).normal(size=(40, 3)) * [12, 7, 3]
    return trimesh.convex.convex_hull(points)


def moved(mesh, T):
    out = mesh.copy()
    out.apply_transform(T)
    return out


def known_pose():
    """A part flipped over, spun 37 degrees on the bed and moved, as a slicer might."""
    flip = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    spin = trimesh.transformations.rotation_matrix(np.radians(37), [0, 0, 1])
    T = spin @ flip
    T[:3, 3] = [120.0, -45.5, 8.25]
    return T


def test_fit_recovers_a_flip_spin_and_move():
    src = lumpy_part()
    T = known_pose()
    dst = moved(src.subdivide(), T)   # different triangles, same surface
    found, err = fit(src, dst)
    assert err < 1e-3
    np.testing.assert_allclose(trimesh.transform_points(src.vertices, found),
                               trimesh.transform_points(src.vertices, T), atol=1e-3)


def test_fit_reports_a_different_shape():
    src = lumpy_part()
    dst = moved(src.subdivide(), known_pose())
    dst.vertices[dst.vertices[:, 2] > dst.center_mass[2] + 2] += [0, 0, 0.5]   # a raised top
    _, err = fit(src, dst)
    assert err > 0.05


def test_same_triangles_are_matched_vertex_to_vertex():
    src = lumpy_part()
    T = known_pose()
    found, err = match_vertices(src, moved(src, T))
    assert err < 1e-9
    np.testing.assert_allclose(found, T, atol=1e-9)
    assert match_vertices(src, src.subdivide()) == (None, float("inf"))


def test_part_file_names_map_to_step_solids_and_back():
    assert solid_name("counter-gear") == "counter-gear"
    assert solid_name("simple-counter-face-two-colour") == "simple-counter-face"
    for stem, solid in FILE_TO_SOLID.items():
        assert solid_name(stem) == solid
        assert file_stem(solid) == stem
