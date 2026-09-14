import bpy
import json


ARMATURE_NAME = "卡提希娅_arm"
FOOT_CONTROLS = ("足ＩＫ.R", "足ＩＫ.L")
POLE_CONTROLS = ("膝盖朝向.R", "膝盖朝向.L")
IK_COLLECTION = "【主控】脚部IK"

scene = bpy.context.scene
arm = bpy.data.objects[ARMATURE_NAME]

bpy.context.view_layer.objects.active = arm
arm.select_set(True)
if arm.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")

collection = arm.data.collections.get(IK_COLLECTION)
if collection:
    collection.is_visible = True

bpy.ops.pose.select_all(action="DESELECT")
for name in FOOT_CONTROLS:
    bone = arm.data.bones.get(name)
    if bone:
        bone.hide = False
        arm.pose.bones[name].select = True
for name in POLE_CONTROLS:
    bone = arm.data.bones.get(name)
    if bone:
        bone.hide = False

arm.data.bones.active = arm.data.bones.get(FOOT_CONTROLS[0])
bpy.context.view_layer.update()

report = {}
for side in ("R", "L"):
    knee = arm.pose.bones[f"ひざ.{side}"]
    constraints = [c for c in knee.constraints if c.type == "IK" and c.chain_count == 2]
    report[side] = {
        "foot_control": f"足ＩＫ.{side}",
        "pole_control": f"膝盖朝向.{side}",
        "main_leg_ik_count": len(constraints),
        "target": constraints[0].subtarget if constraints else None,
        "pole": constraints[0].pole_subtarget if constraints else None,
        "chain_count": constraints[0].chain_count if constraints else None,
        "influence": constraints[0].influence if constraints else None,
    }

bpy.ops.wm.save_as_mainfile(filepath=r"D:\project\blender_learning\renders\carthya_character_only_keyframing.blend")
print(json.dumps({"saved": bpy.data.filepath, "mode": arm.mode, "ik": report}, ensure_ascii=False, indent=2))
