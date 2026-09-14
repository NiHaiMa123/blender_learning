import bpy
import json
import math
from mathutils import Matrix, Vector


ARMATURE_NAME = "卡提希娅_arm"
SIDES = {
    "R": {
        "thigh": "足.R",
        "knee": "ひざ.R",
        "ankle": "足首.R",
        "foot": "足ＩＫ.R",
        "pole": "膝盖朝向.R",
    },
    "L": {
        "thigh": "足.L",
        "knee": "ひざ.L",
        "ankle": "足首.L",
        "foot": "足ＩＫ.L",
        "pole": "膝盖朝向.L",
    },
}

TESTS = [
    ("forward_up", Vector((0.0, -0.18, 0.18)), math.radians(18)),
    ("back_up", Vector((0.0, 0.13, 0.12)), math.radians(-14)),
    ("out_up", Vector((0.13, -0.05, 0.10)), math.radians(12)),
    ("compress", Vector((0.0, -0.08, 0.28)), math.radians(-8)),
]


def mat_max_delta(a, b):
    return max(abs(a[i][j] - b[i][j]) for i in range(4) for j in range(4))


def bone_world_point(arm, pb, which="head"):
    p = pb.head if which == "head" else pb.tail
    return arm.matrix_world @ p


def evaluate_metrics(arm, side, rest_other, rest_pelvis):
    names = SIDES[side]
    thigh = arm.pose.bones[names["thigh"]]
    knee = arm.pose.bones[names["knee"]]
    ankle = arm.pose.bones[names["ankle"]]
    foot = arm.pose.bones[names["foot"]]
    pole = arm.pose.bones[names["pole"]]

    hip_p = bone_world_point(arm, thigh, "head")
    knee_p = bone_world_point(arm, knee, "head")
    ankle_p = bone_world_point(arm, ankle, "head")
    target_p = arm.matrix_world @ foot.matrix.translation
    pole_p = arm.matrix_world @ pole.matrix.translation

    upper = (hip_p - knee_p).normalized()
    lower = (ankle_p - knee_p).normalized()
    bend_angle = math.degrees(math.acos(max(-1.0, min(1.0, upper.dot(lower)))))

    axis = (ankle_p - hip_p).normalized()
    knee_plane = knee_p - hip_p
    knee_plane -= axis * knee_plane.dot(axis)
    pole_plane = pole_p - hip_p
    pole_plane -= axis * pole_plane.dot(axis)
    pole_alignment = 1.0
    if knee_plane.length > 1e-8 and pole_plane.length > 1e-8:
        pole_alignment = knee_plane.normalized().dot(pole_plane.normalized())

    other = "L" if side == "R" else "R"
    other_delta = max(
        mat_max_delta(arm.pose.bones[SIDES[other][key]].matrix.copy(), rest_other[key])
        for key in ("thigh", "knee", "ankle")
    )
    pelvis_delta = mat_max_delta(arm.pose.bones["下半身"].matrix.copy(), rest_pelvis)

    return {
        "ankle_target_error": (ankle_p - target_p).length,
        "pole_alignment": pole_alignment,
        "knee_bend_degrees": bend_angle,
        "opposite_leg_delta": other_delta,
        "pelvis_delta": pelvis_delta,
    }


arm = bpy.data.objects[ARMATURE_NAME]
scene = bpy.context.scene
original_mode = arm.mode
original_active = bpy.context.view_layer.objects.active
original_basis = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}

try:
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    bpy.context.view_layer.update()

    baseline = {
        side: {
            key: arm.pose.bones[SIDES[side][key]].matrix.copy()
            for key in ("thigh", "knee", "ankle")
        }
        for side in SIDES
    }
    pelvis_baseline = arm.pose.bones["下半身"].matrix.copy()
    basis_baseline = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
    results = []

    for side, names in SIDES.items():
        side_sign = 1.0 if side == "R" else -1.0
        for label, offset, zrot in TESTS:
            for pb in arm.pose.bones:
                pb.matrix_basis = basis_baseline[pb.name].copy()
            bpy.context.view_layer.update()

            foot = arm.pose.bones[names["foot"]]
            wm = arm.matrix_world @ foot.matrix
            move = Vector((offset.x * side_sign, offset.y, offset.z))
            rot = Matrix.Rotation(zrot * side_sign, 4, "Z")
            new_wm = Matrix.Translation(move) @ wm @ rot
            foot.matrix = arm.matrix_world.inverted() @ new_wm
            bpy.context.view_layer.update()

            other = "L" if side == "R" else "R"
            metrics = evaluate_metrics(arm, side, baseline[other], pelvis_baseline)
            metrics.update({"side": side, "test": label})
            results.append(metrics)

    limits = {
        "max_target_error": max(r["ankle_target_error"] for r in results),
        "min_pole_alignment": min(r["pole_alignment"] for r in results),
        "min_knee_bend_degrees": min(r["knee_bend_degrees"] for r in results),
        "max_knee_bend_degrees": max(r["knee_bend_degrees"] for r in results),
        "max_opposite_leg_delta": max(r["opposite_leg_delta"] for r in results),
        "max_pelvis_delta": max(r["pelvis_delta"] for r in results),
    }
    limits["passed"] = (
        limits["max_target_error"] < 0.001
        and limits["min_pole_alignment"] > 0.75
        and limits["max_opposite_leg_delta"] < 1e-5
        and limits["max_pelvis_delta"] < 1e-5
    )
    print(json.dumps({"summary": limits, "tests": results}, ensure_ascii=False, indent=2))
finally:
    for pb in arm.pose.bones:
        if pb.name in original_basis:
            pb.matrix_basis = original_basis[pb.name].copy()
    bpy.context.view_layer.update()
    if original_mode != arm.mode:
        bpy.ops.object.mode_set(mode=original_mode)
    bpy.context.view_layer.objects.active = original_active

