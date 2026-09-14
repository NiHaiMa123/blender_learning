import bpy
import json

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
mw = obj.matrix_world
report = {
    "location": [round(v, 5) for v in obj.location],
    "scale": [round(v, 5) for v in obj.scale],
    "rotation": [round(v, 5) for v in obj.rotation_euler],
    "parent": obj.parent.name if obj.parent else None,
}
metal_slot = next((i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == "metal leg"), None)
skin_slot = next((i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == "皮肤"), None)
# world bbox of metal ring faces
ws = []
for poly in obj.data.polygons:
    if poly.material_index == metal_slot:
        ws.append(mw @ poly.center)
if ws:
    report["ring_world_bbox"] = {
        "x": [round(min(v.x for v in ws), 4), round(max(v.x for v in ws), 4)],
        "y": [round(min(v.y for v in ws), 4), round(max(v.y for v in ws), 4)],
        "z": [round(min(v.z for v in ws), 4), round(max(v.z for v in ws), 4)],
    }
# world z of skin faces across thigh front (local x<-0.02), binned
import math
zbins = {}
for poly in obj.data.polygons:
    if poly.material_index != skin_slot:
        continue
    c = poly.center
    if c.x < -0.02:
        wz = round((mw @ c).z, 2)
        zbins[wz] = zbins.get(wz, 0) + 1
report["skin_R_thigh_world_z_counts"] = dict(sorted(zbins.items()))
print(json.dumps(report, ensure_ascii=False, indent=1))
