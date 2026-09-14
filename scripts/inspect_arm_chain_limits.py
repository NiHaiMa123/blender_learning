import bpy
import json

arm = bpy.data.objects["卡提希娅_arm"]
names = []
for side in ("R", "L"):
    names.extend([f"肩C.{side}", f"腕.{side}", f"腕捩.{side}", f"ひじ.{side}", f"手捩.{side}", f"手首.{side}"])

out = {}
for name in names:
    pb = arm.pose.bones[name]
    b = arm.data.bones[name]
    out[name] = {
        "parent": b.parent.name if b.parent else None,
        "connected": b.use_connect,
        "inherit_rotation": b.use_inherit_rotation,
        "rotation_mode": pb.rotation_mode,
        "lock_ik": [pb.lock_ik_x, pb.lock_ik_y, pb.lock_ik_z],
        "use_ik_limits": [pb.use_ik_limit_x, pb.use_ik_limit_y, pb.use_ik_limit_z],
        "ik_min": [pb.ik_min_x, pb.ik_min_y, pb.ik_min_z],
        "ik_max": [pb.ik_max_x, pb.ik_max_y, pb.ik_max_z],
        "ik_stiffness": [pb.ik_stiffness_x, pb.ik_stiffness_y, pb.ik_stiffness_z],
        "head": list(pb.head),
        "tail": list(pb.tail),
        "bone_length": b.length,
    }
print(json.dumps(out, ensure_ascii=False, indent=2))
