import bpy
import json

coll = bpy.data.collections.get("路灯")
rows = []
if coll is not None:
    for o in coll.all_objects:
        if o.type not in ("LIGHT", "MESH"):
            continue
        world = o.matrix_world.translation
        rows.append({
            "name": o.name, "type": o.type,
            "parent": o.parent.name if o.parent else None,
            "local": [round(v, 3) for v in o.location],
            "world": [round(v, 3) for v in world],
        })
rows.sort(key=lambda r: (r["type"], r["name"]))
print(json.dumps(rows, ensure_ascii=False, indent=1))
