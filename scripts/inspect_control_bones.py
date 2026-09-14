import bpy
import json
import re

arm = bpy.data.objects["卡提希娅_arm"]
pattern = re.compile(r"^(センター|グルーブ|腰$|下半身$|上半身\d*$|首$|頭$|肩\.?[LR]$|腕\.?[LR]$|ひじ\.?[LR]$|手首\.?[LR]$|足\.?[LR]$|ひざ\.?[LR]$|足首\.?[LR]$|足ＩＫ\.?[LR]$|つま先ＩＫ\.?[LR]$|親指|人指|中指|薬指|小指)")

rows = []
for pb in arm.pose.bones:
    if pb.name.startswith(("_dummy", "_shadow")):
        continue
    if pattern.search(pb.name):
        rows.append({
            "name": pb.name,
            "parent": pb.parent.name if pb.parent else None,
            "head": [round(float(v), 4) for v in pb.head],
            "tail": [round(float(v), 4) for v in pb.tail],
            "rotation_mode": pb.rotation_mode,
            "constraints": [c.type for c in pb.constraints],
        })

print(json.dumps(rows, ensure_ascii=False, indent=2))
