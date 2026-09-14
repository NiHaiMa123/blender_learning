import bpy
import json

arm = bpy.data.objects.get("卡提希娅_arm")
if not arm or arm.type != "ARMATURE":
    raise RuntimeError("Armature 卡提希娅_arm not found")

rows = []
for pb in arm.pose.bones:
    if pb.parent:
        parent = pb.parent.name
    else:
        parent = None
    rows.append({
        "name": pb.name,
        "parent": parent,
        "head": [round(float(v), 4) for v in pb.head],
        "tail": [round(float(v), 4) for v in pb.tail],
        "constraints": [
            {"name": c.name, "type": c.type, "target": c.target.name if getattr(c, "target", None) else None,
             "subtarget": getattr(c, "subtarget", "")}
            for c in pb.constraints
        ],
    })

print(json.dumps({"armature": arm.name, "bone_count": len(rows), "bones": rows}, ensure_ascii=False, indent=2))
