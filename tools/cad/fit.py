"""Rigid fit of one mesh onto another, for meshes that were only moved, turned or flipped over."""

import itertools

import numpy as np
import trimesh
from scipy.spatial import cKDTree

SPIN_STEP = 1.0   # degrees between trial turns about each principal axis; ICP does the rest
REFINE = 30       # most promising trial poses refined in finer turns
CANDIDATES = 3    # best refined poses polished with ICP


def rotation(axis, deg):
    """3x3 rotation by `deg` about the unit vector `axis`."""
    return trimesh.transformations.rotation_matrix(np.radians(deg), axis)[:3, :3]


def matrix(R, t):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


def surface_rms(src, dst, T=None, n=3000):
    """RMS distance (mm) from points sampled on `src`, moved by T, to the surface of `dst`.
    Slow when the two are far apart; place them first."""
    probe = src.sample(n, seed=1)
    if T is not None:
        probe = trimesh.transform_points(probe, T)
    _, d, _ = trimesh.proximity.closest_point(dst, probe)
    return float(np.sqrt((d ** 2).mean()))


def vertex_rms(src, dst, T):
    """RMS distance (mm) from the vertices of `dst`, moved back by T, to the surface of `src`.
    The vertices of an exported mesh lie on the surface it was made from, so a coarse
    mesh is not marked down for the size of its facets."""
    pts = trimesh.transform_points(dst.vertices, np.linalg.inv(T))
    _, d, _ = trimesh.proximity.closest_point(src, pts)
    return float(np.sqrt((d ** 2).mean()))


def match_vertices(src, dst):
    """Exact rigid T and vertex RMS for two meshes with the same triangles and vertex order
    (a project object and its part file), or (None, inf) if they are not like that."""
    if src.faces.shape != dst.faces.shape or not np.array_equal(src.faces, dst.faces):
        return None, float("inf")
    a, b = src.vertices, dst.vertices
    ca, cb = a.mean(0), b.mean(0)
    U, _, Vt = np.linalg.svd((a - ca).T @ (b - cb))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    T = matrix(R, cb - R @ ca)
    d = np.linalg.norm(trimesh.transform_points(a, T) - b, axis=1)
    return T, float(np.sqrt((d ** 2).mean()))


def mass_frame(mesh):
    """(centre of mass, 3x3 inertia matrix about it) of a closed mesh."""
    return mesh.center_mass, mesh.moment_inertia


def principal_axes(inertia):
    """Principal axes as rows, smallest moment first."""
    _, vectors = np.linalg.eigh(inertia)
    return vectors.T


def trial_rotations(src_axes, dst_axes):
    """(axis, base rotation) pairs: each base maps the principal axes of src onto those of
    dst, for every sign choice that is a proper rotation. The caller also turns each base
    about every principal axis, which covers round parts whose axes are not well defined."""
    for signs in itertools.product((1, -1), repeat=3):
        base = dst_axes.T @ np.diag(signs) @ src_axes
        if np.linalg.det(base) > 0:
            for axis in dst_axes:
                yield axis, base


def fit(src, dst, src_frame=None):
    """Best rigid 4x4 T with T(src) ~ dst, and its error: vertex_rms in mm.

    Meshes with the same triangles are matched vertex to vertex. Otherwise the centres of
    mass are put together, every alignment of the principal axes is tried with turns of
    SPIN_STEP about each axis, the most promising poses are refined, and the best few are
    polished with ICP. `src_frame` (centre, inertia) overrides the mass properties of src,
    for a STEP solid whose mesh may not be closed.
    Parts that are nearly symmetric may come out turned about their own axis by a
    symmetry step, which leaves their footprint on the bed unchanged.
    """
    T, err = match_vertices(src, dst)
    if T is not None:
        return T, err
    c_src, i_src = src_frame or mass_frame(src)
    c_dst, i_dst = mass_frame(dst)
    probe = src.sample(3000, seed=1)
    rough = cKDTree(dst.sample(20000, seed=2))    # quick, for sorting out the trial poses
    dense = cKDTree(dst.sample(200000, seed=3))   # finer, for refining the best of them

    def score(R, pts, tree):
        """(RMS to the target samples, T) for rotation R about the centres of mass."""
        t = c_dst - R @ c_src
        d, _ = tree.query(pts @ R.T + t)
        return float(np.sqrt((d ** 2).mean())), matrix(R, t)

    coarse = []
    for axis, base in trial_rotations(principal_axes(i_src), principal_axes(i_dst)):
        for deg in np.arange(0, 360, SPIN_STEP):
            coarse.append((score(rotation(axis, deg) @ base, probe[::30], rough)[0], deg, tuple(axis), base))
    refined = []
    for _, deg, axis, base in sorted(coarse, key=lambda x: x[:2])[:REFINE]:
        refined.append(min((score(rotation(axis, deg + d) @ base, probe[::3], dense)
                            for d in np.arange(-SPIN_STEP, SPIN_STEP, SPIN_STEP / 20)), key=lambda p: p[0]))
    polished = []
    for _, T0 in sorted(refined, key=lambda p: p[0])[:CANDIDATES]:
        T, _, _ = trimesh.registration.icp(probe[::3], dst, initial=T0, threshold=1e-7,
                                           max_iterations=30, reflection=False, scale=False)
        polished.append((surface_rms(src, dst, T), T))
    T = min(polished, key=lambda p: p[0])[1]
    # finish the winner the other way round: the target's vertices lie on its true surface,
    # so pulling them onto src is not thrown off by the size of the target's facets
    rng = np.random.default_rng(4)
    verts = dst.vertices[rng.choice(len(dst.vertices), min(3000, len(dst.vertices)), replace=False)]
    back, _, _ = trimesh.registration.icp(verts, src, initial=np.linalg.inv(T), threshold=1e-10,
                                          max_iterations=50, reflection=False, scale=False)
    T = np.linalg.inv(back)
    return T, vertex_rms(src, dst, T)
