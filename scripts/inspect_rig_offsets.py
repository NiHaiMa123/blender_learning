import bpy
import json

parent = bpy.data.objects.get("空物体.027")
rows = []
for o in bpy.data.objects:
    if o.parent == parent:
        rows.append({"name": o.name, "type": o.type,
                     "local": [round(v, 3) for v in o.location]})
rows.sort(key=lambda r: r["name"])
print(json.dumps(rows, ensure_ascii=False, indent=1))
