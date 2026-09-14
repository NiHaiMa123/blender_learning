import bpy
arm = bpy.data.objects["卡提希娅_arm"]
bone = arm.data.bones.get("足ＩＫ.R")
pb = arm.pose.bones.get("足ＩＫ.R")
print({
    "bone_select_attrs": [a for a in dir(bone) if "select" in a.lower() or "active" in a.lower()],
    "pose_bone_select_attrs": [a for a in dir(pb) if "select" in a.lower() or "active" in a.lower()],
    "arm_bones_attrs": [a for a in dir(arm.data.bones) if "select" in a.lower() or "active" in a.lower()],
})
