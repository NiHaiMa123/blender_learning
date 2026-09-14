import bpy
import json

empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE" and o.parent is not None and o.parent.name == empty.name), None)
out = {}
for side in ("R", "L"):
    out[side] = {}
    for name in (f"肩.{side}", f"腕.{side}", f"ひじ.{side}", f"手首.{side}"):
        pb = arm.pose.bones.get(name)
        if pb is not None:
            out[side][name] = {
                "head": [round(float(v), 4) for v in pb.head],
                "tail": [round(float(v), 4) for v in pb.tail],
                "length": round(float(pb.length), 4),
            }
print(json.dumps(out, ensure_ascii=False, indent=1))
