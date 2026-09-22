"""Pure gear maths for the Infidex frame-counter train (no CAD dependencies).

Train: sprocket pinion -> [wheel+pinion] x 3 idlers -> dial wheel.
Units are mm and degrees. Angles follow the body's XY axes.
"""
from dataclasses import dataclass
import math


class LayoutError(ValueError):
    pass


@dataclass(frozen=True)
class GearSpec:
    teeth: int
    module: float
    pressure_angle_deg: float = 20.0
    thinning: float = 0.125      # removed from tooth thickness (backlash share)
    tip_reduction: float = 0.0   # radial shave off the tip circle
    shift: float = 0.0           # profile shift coefficient x
    flank_points: int = 12

    @property
    def pitch_r(self):
        return self.module * self.teeth / 2


@dataclass(frozen=True)
class TrainSpec:
    module: float = 0.6
    pressure_angle_deg: float = 20.0
    pinion_teeth: int = 12
    wheel_teeth: tuple = (32, 30, 30, 36)       # one per mesh, sprocket -> dial
    thinning: float = 0.10
    pinion_shift: float = 0.4                    # wheels get the opposite shift
    pinion_tip_reduction: float = 0.10
    wheel_tip_reduction: float = 0.04
    sprocket_axis: tuple = (73.20, -45.21)
    dial_axis: tuple = (67.70, -63.94)
    idler1_angle_deg: float = -90.74            # direction sprocket -> idler 1
    idler2_angle_deg: float = -164.0            # direction idler 1 -> idler 2
    idler3_elbow: int = 1                       # which of the two solutions for idler 3
    face_width: float = 2.0
    layer_gap: float = 0.2
    base_z: float = 36.8                         # underside of idler 1's wheel
    clearance: float = 0.3                       # minimum gap to non-meshing gears
    bores: tuple = (4.4, 4.0, 3.0, 3.2)          # idler 1-3, dial
    hub_diameter: float = 6.6
    # fixed round parts sharing the bay: (axis index, diameter, z0, z1)
    obstacles: tuple = ((0, 5.4, 30.0, 41.0),     # sprocket-gear hub
                        (4, 17.0, 44.9, 47.6),    # counter dial, lower step
                        (4, 20.0, 47.6, 49.4))    # counter dial face

    def pinion(self):
        return GearSpec(self.pinion_teeth, self.module, self.pressure_angle_deg, self.thinning,
                        self.pinion_tip_reduction, self.pinion_shift)

    def wheel(self, stage):
        return GearSpec(self.wheel_teeth[stage], self.module, self.pressure_angle_deg,
                        self.thinning, self.wheel_tip_reduction, -self.pinion_shift)


# ---------- train ----------

def ratio(t: TrainSpec):
    r = 1.0
    for z in t.wheel_teeth:
        r *= z / t.pinion_teeth
    return r


def centre_distances(t: TrainSpec):
    return [t.module * (t.pinion_teeth + z) / 2 for z in t.wheel_teeth]


def _polar(p, d, deg):
    a = math.radians(deg)
    return (p[0] + d * math.cos(a), p[1] + d * math.sin(a))


def layout(t: TrainSpec):
    """Axes [sprocket, idler1, idler2, idler3, dial]. End axes are fixed."""
    d = centre_distances(t)
    a0, a4 = tuple(t.sprocket_axis), tuple(t.dial_axis)
    a1 = _polar(a0, d[0], t.idler1_angle_deg)
    a2 = _polar(a1, d[1], t.idler2_angle_deg)
    a3 = _circle_intersection(a2, d[2], a4, d[3], t.idler3_elbow)
    return [a0, a1, a2, a3, a4]


def _circle_intersection(c1, r1, c2, r2, elbow):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    L = math.hypot(dx, dy)
    if L > r1 + r2 or L < abs(r1 - r2) or L == 0:
        raise LayoutError(f"idler 3 cannot reach: axes {L:.2f} mm apart, links {r1:.2f} + {r2:.2f} mm")
    a = (r1 * r1 - r2 * r2 + L * L) / (2 * L)
    h = math.sqrt(max(r1 * r1 - a * a, 0.0))
    mx, my = c1[0] + a * dx / L, c1[1] + a * dy / L
    return (mx - elbow * h * dy / L, my + elbow * h * dx / L)


def layers(t: TrainSpec):
    """(axis index, kind, gear, z0, z1) for every toothed body."""
    step = t.face_width + t.layer_gap
    out = [(0, "pinion", t.pinion(), t.base_z, t.base_z + t.face_width)]
    for s in range(4):
        z0 = t.base_z + s * step
        out.append((s + 1, "wheel", t.wheel(s), z0, z0 + t.face_width))
        if s < 3:
            out.append((s + 1, "pinion", t.pinion(), z0 + step, z0 + step + t.face_width))
    return out


def collisions(t: TrainSpec):
    """Pairs of bodies that overlap in z and whose tip circles come closer than
    `clearance` without being a meshing pair."""
    axes = layout(t)
    bodies = [(a, k, tip_diameter(g), z0, z1) for a, k, g, z0, z1 in layers(t)]
    bodies += [(a, "fixed", d, z0, z1) for a, d, z0, z1 in t.obstacles]
    meshing = {(0, 1)} | {(s, s + 1) for s in range(1, 4)}
    problems = []
    for i, (ai, ki, gi, zi0, zi1) in enumerate(bodies):
        for aj, kj, gj, zj0, zj1 in bodies[i + 1:]:
            if ai == aj or min(zi1, zj1) <= max(zi0, zj0):
                continue
            pair = tuple(sorted((ai, aj)))
            if pair in meshing and {ki, kj} == {"wheel", "pinion"}:
                continue
            gap = math.dist(axes[ai], axes[aj]) - gi / 2 - gj / 2
            if gap < t.clearance:
                problems.append((ai, ki, aj, kj, round(gap, 3)))
    return problems


def contact_ratio(t: TrainSpec, stage, spread=0.0):
    """Transverse contact ratio of mesh `stage`, with the axes `spread` mm further
    apart than designed (print and fit tolerance). Below 1.0 the teeth lose contact."""
    p, w = t.pinion(), t.wheel(stage)
    alpha = math.radians(t.pressure_angle_deg)
    a0 = centre_distances(t)[stage]
    a = a0 + spread
    alpha_w = math.acos(a0 / a * math.cos(alpha))
    reach = sum(math.sqrt((tip_diameter(g) / 2) ** 2 - (g.pitch_r * math.cos(alpha)) ** 2) for g in (p, w))
    return (reach - a * math.sin(alpha_w)) / (math.pi * t.module * math.cos(alpha))


def backlash(t: TrainSpec, stage):
    return t.pinion().thinning + t.wheel(stage).thinning


# ---------- single gear ----------

def tip_diameter(g: GearSpec):
    return g.module * (g.teeth + 2 + 2 * g.shift) - 2 * g.tip_reduction


def root_diameter(g: GearSpec):
    return g.module * (g.teeth - 2.5 + 2 * g.shift)


def tip_root_clearance(t: TrainSpec, stage):
    """Smallest radial gap between a tip and the mating root at mesh `stage`."""
    c = centre_distances(t)[stage]
    p, w = t.pinion(), t.wheel(stage)
    return min(c - tip_diameter(p) / 2 - root_diameter(w) / 2,
               c - tip_diameter(w) / 2 - root_diameter(p) / 2)


def _inv(a):
    return math.tan(a) - a


def profile(g: GearSpec):
    """Closed outline as (x, y) points, counter-clockwise, tooth 0 centred on +X."""
    alpha = math.radians(g.pressure_angle_deg)
    rp = g.pitch_r
    rb = rp * math.cos(alpha)
    ra = tip_diameter(g) / 2
    rf = root_diameter(g) / 2
    pitch_angle = 2 * math.pi / g.teeth
    # half tooth angle at the pitch circle, then referred to the base circle
    s = math.pi * g.module / 2 + 2 * g.shift * g.module * math.tan(alpha) - g.thinning
    half_pitch = s / (2 * rp)
    half_base = half_pitch + _inv(alpha)
    r_start = max(rb, rf)
    pts = []
    for k in range(g.teeth):
        c = k * pitch_angle
        flank = []
        for i in range(g.flank_points + 1):
            r = r_start + (ra - r_start) * i / g.flank_points
            phi = math.acos(min(rb / r, 1.0))
            flank.append((r, half_base - _inv(phi)))
        # root arc from previous tooth, radial drop to the flank start
        right = [(r, c - th) for r, th in flank]            # rising flank, clockwise side
        left = [(r, c + th) for r, th in reversed(flank)]   # falling flank
        tooth = [(rf, c - half_base)] if rf < r_start else []
        tooth += right
        # tip arc
        a0, a1 = c - flank[-1][1], c + flank[-1][1]
        tooth += [(ra, a0 + (a1 - a0) * j / 3) for j in range(1, 3)]
        tooth += left
        if rf < r_start:
            tooth.append((rf, c + half_base))
        # root arc to the next tooth
        n_root = 4
        g0, g1 = c + half_base, c + pitch_angle - half_base
        tooth += [(rf, g0 + (g1 - g0) * j / n_root) for j in range(1, n_root)]
        pts += [(r * math.cos(a), r * math.sin(a)) for r, a in tooth]
    return pts


def tooth_thickness_at_pitch(g: GearSpec):
    """Arc thickness of tooth 0 measured on the pitch circle from the profile."""
    pts = profile(g)
    rp = g.pitch_r
    angles = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        r0, r1 = math.hypot(x0, y0), math.hypot(x1, y1)
        if (r0 - rp) * (r1 - rp) < 0:
            t = (rp - r0) / (r1 - r0)
            a = math.atan2(y0 + t * (y1 - y0), x0 + t * (x1 - x0))
            if abs(a) < math.pi / g.teeth:
                angles.append(a)
    return (max(angles) - min(angles)) * rp
