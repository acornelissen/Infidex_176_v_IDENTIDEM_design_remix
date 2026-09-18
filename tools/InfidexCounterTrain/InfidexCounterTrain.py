"""Fusion script: build the Infidex counter gear train from the ct_* user parameters.

First run creates the parameters with the rev5 values. Edit them in
Modify > Change Parameters, then run the script again to rebuild.
"""
import importlib
import math
import os
import sys
import traceback

import adsk.core
import adsk.fusion

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gearcalc as gc  # noqa: E402
import params as pm    # noqa: E402

CM = 0.1  # Fusion works in cm
GROUP = "CT counter train"  # timeline group holding everything the script builds


def run(context):
    ui = None
    try:
        importlib.reload(gc)
        importlib.reload(pm)
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            ui.messageBox("Open a Fusion design first.")
            return
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        values = _read_parameters(design)
        spec = pm.to_spec(values)
        try:
            axes = gc.layout(spec)
        except gc.LayoutError as e:
            ui.messageBox(f"Counter train not rebuilt:\n{e}")
            return
        clashes = gc.collisions(spec)
        if clashes:
            ui.messageBox("Counter train not rebuilt, parts would clash:\n" +
                          "\n".join(f"axis {a} {ka} vs axis {b} {kb}: gap {g} mm" for a, ka, b, kb, g in clashes))
            return
        _build(design, spec, axes)
        ui.messageBox(_summary(spec, axes))
    except Exception:
        if ui:
            ui.messageBox("Counter train script failed:\n" + traceback.format_exc())


def _read_parameters(design):
    params = design.userParameters
    values = {}
    for p in pm.PARAMETERS:
        existing = params.itemByName(p.name)
        if existing is None:
            expr = f"{p.value} {p.unit}".strip()
            existing = params.add(p.name, adsk.core.ValueInput.createByString(expr), p.unit, p.comment)
        # .value is in Fusion's internal units: cm and radians
        raw = existing.value
        values[p.name] = raw / CM if p.unit == "mm" else math.degrees(raw) if p.unit == "deg" else raw
    return values


def _build(design, spec, axes):
    root = design.rootComponent
    _remove_previous(design)
    first = design.timeline.count
    names = ["CT sprocket pinion (tool body)", "CT idler 1", "CT idler 2", "CT idler 3", "CT dial wheel (tool body)"]
    by_axis = {}
    for axis, kind, gear, z0, z1 in gc.layers(spec):
        by_axis.setdefault(axis, []).append((kind, gear, z0, z1))
    for axis, layers in by_axis.items():
        comp = _target_component(root, names[axis])
        bore = spec.bores[axis - 1] if axis >= 1 else 0.0
        body = None
        for kind, gear, z0, z1 in layers:
            b = _gear_layer(comp, gear, axes[axis], z0, z1 - z0, bore, f"{names[axis]} {kind}")
            if body is None:
                body = b
            else:
                tools = adsk.core.ObjectCollection.create()
                tools.add(b)
                comb = comp.features.combineFeatures.createInput(body, tools)
                comb.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
                comp.features.combineFeatures.add(comb)
        body.name = names[axis]
    if design.timeline.count > first:
        design.timeline.timelineGroups.add(first, design.timeline.count - 1).name = GROUP


def _target_component(root, name):
    """A sub-component where the document allows it (assemblies), otherwise the root
    (Part Design documents hold a single component)."""
    try:
        comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        comp.name = name
        return comp
    except RuntimeError:
        return root


def _remove_previous(design):
    for occ in list(design.rootComponent.occurrences):
        if occ.component.name.startswith("CT "):
            occ.deleteMe()
    groups = design.timeline.timelineGroups
    for g in reversed([groups.item(i) for i in range(groups.count)]):
        if g.name == GROUP:
            g.deleteMe(True)


def _gear_layer(comp, gear, centre, z0, height, bore, label):
    planes = comp.constructionPlanes
    pin = planes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z0 * CM))
    plane = planes.add(pin)
    plane.isLightBulbOn = False
    sk = comp.sketches.add(plane)
    sk.isComputeDeferred = True
    cx, cy = centre
    pts = [adsk.core.Point3D.create((cx + x) * CM, (cy + y) * CM, 0) for x, y in gc.profile(gear)]
    lines = sk.sketchCurves.sketchLines
    first = prev = lines.addByTwoPoints(pts[0], pts[1])
    for p in pts[2:]:
        prev = lines.addByTwoPoints(prev.endSketchPoint, p)
    lines.addByTwoPoints(prev.endSketchPoint, first.startSketchPoint)
    if bore > 0:
        sk.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(cx * CM, cy * CM, 0), bore / 2 * CM)
    sk.isComputeDeferred = False
    profile = max(sk.profiles, key=lambda pr: pr.areaProperties().area)
    ext = comp.features.extrudeFeatures.addSimple(
        profile, adsk.core.ValueInput.createByReal(height * CM),
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    body = ext.bodies.item(0)
    body.name = label
    return body


def _summary(spec, axes):
    lines = [f"Counter train rebuilt. Ratio {gc.ratio(spec):.3f}:1"]
    for s, d in enumerate(gc.centre_distances(spec)):
        lines.append(f"mesh {s + 1}: {spec.pinion_teeth}:{spec.wheel_teeth[s]}  centres {d:.3f} mm  "
                     f"tip/root clearance {gc.tip_root_clearance(spec, s):.3f} mm  backlash {gc.backlash(spec, s):.3f} mm")
    for i, (x, y) in enumerate(axes):
        lines.append(f"axis {i}: X {x:.3f}  Y {y:.3f}")
    return "\n".join(lines)
