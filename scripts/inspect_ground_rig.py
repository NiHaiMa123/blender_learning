import bpy
import json
from mathutils import Vector

report = {}

# ground/path meshes: search by name
cands = [o for o in bpy.data.objects
         if o.type == "MESH" and any(k in o.name for k in ("路", "地面", "砖", "Road", "Ground", " Pav", "河岸"))]
report["ground_candidates"] = []
for o in cands[:15]:
    ws = [o.matrix_world @ v.co for v in o.data.vertices] if o.data and len(o.data.vertices) else []
    if ws:
        report["ground_candidates"].append({
            "name": o.name,
            "z": [round(min(v.z for v in ws), 3), round(max(v.z for v in ws), 3)],
            "verts": len(ws),
        })

# raycast ground at placement spot
deps = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene
hit, loc, *_ = scene.ray_cast(deps, Vector((1.0, -7.0, 5.0)), Vector((0, 0, -1)))
report["placement_ground"] = {"hit": hit, "z": round(float(loc.z), 3) if hit else None}

# rig structure
rig = bpy.data.collections.get("人物灯光（b站搜三分仪打光教程）")
rows = []
if rig is not None:
    for o in rig.all_objects:
        rows.append({"name": o.name, "type": o.type,
                     "parent": o.parent.name if o.parent else None,
                     "world": [round(v, 3) for v in o.matrix_world.translation]})
rows.sort(key=lambda r: (str(r["parent"]), r["name"]))
report["rig"] = rows

print(json.dumps(report, ensure_ascii=False, indent=1))
