import bpy
import json
import math
from mathutils import Matrix, Vector


arm = bpy.data.objects["卡提希娅_arm"]
if arm.mode != "POSE":
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")

original_basis = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
bpy.context.view_layer.update()
baseline = {
    name: arm.pose.bones[name].matrix.copy()
    for side in ("R", "L")
    for name in (f"腕.{side}", f"腕捩.{side}", f"ひじ.{side}", f"手捩.{side}", f"手首.{side}")
}
torso_baseline = {name: arm.pose.bones[name].matrix.copy() for name in ("上半身", "上半身2", "首", "下半身")}

tests = [
    ("front_up", Vector((0.07, -0.14, 0.10)), 24),
    ("inward_up", Vector((0.14, -0.05, 0.10)), -18),
    ("near_extension", Vector((0.012, -0.008, 0.005)), 16),
    ("deep_bend", Vector((0.20, -0.12, 0.16)), -28),
]

def mat_delta(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))

def rotation_alignment(a, b):
    return abs(a.to_quaternion().dot(b.to_quaternion()))

results = []
try:
    for side in ("R", "L"):
        sign = 1.0 if side == "R" else -1.0
        for label, offset, rot_degrees in tests:
            for name, basis in original_basis.items():
                arm.pose.bones[name].matrix_basis = basis.copy()
            bpy.context.view_layer.update()

            hand = arm.pose.bones[f"手部IK.{side}"]
            matrix = hand.matrix.copy()
            move = Vector((offset.x * sign, offset.y, offset.z))
            matrix.translation += move
            pos = matrix.translation.copy()
            matrix = Matrix.Translation(pos) @ Matrix.Rotation(math.radians(rot_degrees * sign), 4, "Z") @ Matrix.Translation(-pos) @ matrix
            hand.matrix = matrix
            bpy.context.view_layer.update()

            upper = arm.pose.bones[f"腕.{side}"]
            elbow = arm.pose.bones[f"ひじ.{side}"]
            wrist = arm.pose.bones[f"手首.{side}"]
            pole = arm.pose.bones[f"手肘朝向.{side}"]
            shoulder_p = upper.head.copy()
            elbow_p = elbow.head.copy()
            wrist_p = wrist.head.copy()
            target_p = hand.head.copy()
            axis = wrist_p - shoulder_p
            projection = shoulder_p + axis * ((elbow_p - shoulder_p).dot(axis) / max(axis.length_squared, 1e-12))
            bend = elbow_p - projection
            pole_dir = pole.head - projection
            alignment = bend.normalized().dot(pole_dir.normalized()) if bend.length > 1e-8 and pole_dir.length > 1e-8 else 0.0

            upper_dir = (shoulder_p - elbow_p).normalized()
            lower_dir = (wrist_p - elbow_p).normalized()
            bend_angle = math.degrees(math.acos(max(-1.0, min(1.0, upper_dir.dot(lower_dir)))))
            other = "L" if side == "R" else "R"
            other_delta = max(
                mat_delta(arm.pose.bones[f"{name}.{other}"].matrix, baseline[f"{name}.{other}"])
                for name in ("腕", "腕捩", "ひじ", "手捩", "手首")
            )
            torso_delta = max(mat_delta(arm.pose.bones[n].matrix, torso_baseline[n]) for n in torso_baseline)
            results.append({
                "side": side,
                "test": label,
                "wrist_target_error": (wrist_p - target_p).length,
                "pole_alignment": alignment,
                "elbow_bend_degrees": bend_angle,
                "wrist_rotation_alignment": rotation_alignment(wrist.matrix, hand.matrix),
                "opposite_arm_delta": other_delta,
                "torso_delta": torso_delta,
            })

    summary = {
        "max_target_error": max(x["wrist_target_error"] for x in results),
        "min_pole_alignment": min(x["pole_alignment"] for x in results),
        "min_elbow_bend_degrees": min(x["elbow_bend_degrees"] for x in results),
        "max_elbow_bend_degrees": max(x["elbow_bend_degrees"] for x in results),
        "min_wrist_rotation_alignment": min(x["wrist_rotation_alignment"] for x in results),
        "max_opposite_arm_delta": max(x["opposite_arm_delta"] for x in results),
        "max_torso_delta": max(x["torso_delta"] for x in results),
    }
    summary["passed"] = (
        summary["max_target_error"] < 0.001
        and summary["min_pole_alignment"] > 0.35
        and summary["min_wrist_rotation_alignment"] > 0.999
        and summary["max_opposite_arm_delta"] < 1e-5
        and summary["max_torso_delta"] < 1e-5
    )
    print(json.dumps({"summary": summary, "tests": results}, ensure_ascii=False, indent=2))
finally:
    for name, basis in original_basis.items():
        arm.pose.bones[name].matrix_basis = basis.copy()
    bpy.context.view_layer.update()
