import bpy
import json
from mathutils import Vector

empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE" and o.parent is not None and o.parent.name == empty.name), None)
out = {}
for side in ("R", "L"):
    upper = arm.pose.bones[f"腕.{side}"]
    fore = arm.pose.bones[f"ひじ.{side}"]
    shoulder = arm.matrix_world @ upper.head
    elbow = arm.matrix_world @ fore.head
    wrist = arm.matrix_world @ fore.tail
    a = (elbow - shoulder).normalized()
    b = (wrist - elbow).normalized()
    out[side] = {
        "shoulder": [round(float(v), 4) for v in shoulder],
        "elbow": [round(float(v), 4) for v in elbow],
        "wrist": [round(float(v), 4) for v in wrist],
        "elbow_angle_deg": round(float(a.angle(b) * 180.0 / 3.141592653589793), 3),
        "chain_length": round(float(upper.length + fore.length), 4),
        "shoulder_wrist_distance": round(float((wrist - shoulder).length), 4),
    }
wr = arm.matrix_world @ arm.pose.bones["ひじ.R"].tail
wl = arm.matrix_world @ arm.pose.bones["ひじ.L"].tail
out["wrist_gap"] = round(float((wr - wl).length), 4)
print(json.dumps(out, ensure_ascii=False, indent=1))
