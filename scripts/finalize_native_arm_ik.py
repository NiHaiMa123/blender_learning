import bpy
import json

arm = bpy.data.objects["卡提希娅_arm"]
bpy.context.view_layer.objects.active = arm
arm.select_set(True)
if arm.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")

collection = arm.data.collections.get("【主控】手部IK")
if collection:
    collection.is_visible = True

bpy.ops.pose.select_all(action="DESELECT")
for side in ("R", "L"):
    for name in (f"手部IK.{side}", f"手肘朝向.{side}"):
        arm.data.bones[name].hide = False
    arm.pose.bones[f"手部IK.{side}"].select = True
arm.data.bones.active = arm.data.bones["手部IK.R"]

report = {}
for side in ("R", "L"):
    elbow = arm.pose.bones[f"ひじ.{side}"]
    iks = [c for c in elbow.constraints if c.type == "IK" and c.name == "原生手臂IK（含手肘朝向）"]
    wrist = arm.pose.bones[f"手首.{side}"]
    copies = [c for c in wrist.constraints if c.type == "COPY_ROTATION" and c.name == "手腕跟随手部IK旋转"]
    report[side] = {
        "ik_count": len(iks),
        "target": iks[0].subtarget if iks else None,
        "pole": iks[0].pole_subtarget if iks else None,
        "chain_count": iks[0].chain_count if iks else None,
        "wrist_rotation_follow": len(copies) == 1,
    }

path = r"D:\project\blender_learning\renders\carthya_character_only_keyframing.blend"
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)
print(json.dumps({"saved": path, "mode": arm.mode, "arms": report}, ensure_ascii=False, indent=2))
