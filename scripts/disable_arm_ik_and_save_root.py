import bpy
import json


ARMATURE_NAME = "卡提希娅_arm"
OUTPUT = r"D:\project\blender_learning\carthya_character_only_keyframing.blend"
ARM_COLLECTION = "【身体】手臂与手腕"
HAND_IK_COLLECTION = "【主控】手部IK"

arm = bpy.data.objects[ARMATURE_NAME]
bpy.context.view_layer.objects.active = arm
arm.hide_set(False)
arm.select_set(True)
if arm.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")
bpy.context.view_layer.update()

# Capture the currently evaluated appearance so disabling IK does not snap the arms.
chains = {
    side: [f"腕.{side}", f"腕捩.{side}", f"ひじ.{side}", f"手捩.{side}", f"手首.{side}"]
    for side in ("R", "L")
}
evaluated = {name: arm.pose.bones[name].matrix.copy() for names in chains.values() for name in names}

disabled = []
for side in ("R", "L"):
    elbow = arm.pose.bones[f"ひじ.{side}"]
    for constraint in elbow.constraints:
        if constraint.type == "IK" and constraint.name == "原生手臂IK（含手肘朝向）":
            constraint.influence = 0.0
            constraint.mute = True
            disabled.append(f"{elbow.name}/{constraint.name}")

    wrist = arm.pose.bones[f"手首.{side}"]
    for constraint in wrist.constraints:
        if constraint.type == "COPY_ROTATION" and constraint.name == "手腕跟随手部IK旋转":
            constraint.influence = 0.0
            constraint.mute = True
            disabled.append(f"{wrist.name}/{constraint.name}")

bpy.context.view_layer.update()

# Bake the evaluated result back into the FK chain in parent-to-child order.
for side in ("R", "L"):
    for name in chains[side]:
        arm.pose.bones[name].matrix = evaluated[name]
        bpy.context.view_layer.update()

def max_delta(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))

pose_deltas = {name: max_delta(arm.pose.bones[name].matrix, evaluated[name]) for name in evaluated}

arm_collection = arm.data.collections.get(ARM_COLLECTION)
if arm_collection:
    arm_collection.is_visible = True
hand_ik_collection = arm.data.collections.get(HAND_IK_COLLECTION)
if hand_ik_collection:
    hand_ik_collection.is_visible = False

bpy.ops.pose.select_all(action="DESELECT")
for side in ("R", "L"):
    arm.pose.bones[f"手首.{side}"].select = True
arm.data.bones.active = arm.data.bones["手首.R"]

for area in bpy.context.window.screen.areas:
    area.tag_redraw()

bpy.ops.wm.save_as_mainfile(filepath=OUTPUT, check_existing=False)

print(json.dumps({
    "saved": bpy.data.filepath,
    "mode": arm.mode,
    "disabled": disabled,
    "max_pose_bake_delta": max(pose_deltas.values()),
    "arm_collection_visible": arm_collection.is_visible if arm_collection else None,
    "hand_ik_collection_visible": hand_ik_collection.is_visible if hand_ik_collection else None,
    "leg_ik_unchanged": True,
}, ensure_ascii=False, indent=2))
