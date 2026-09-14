import bpy
import json

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
uv_layer = obj.data.uv_layers.active
if obj is None or uv_layer is None:
    raise RuntimeError("Character mesh or UV layer not found")

regions = {
    "left_x": {"thigh": [], "calf": []},
    "right_x": {"thigh": [], "calf": []},
}
skin_names = {"皮肤", "Codex Skin Right Leg Lift"}
for poly in obj.data.polygons:
    material = obj.material_slots[poly.material_index].material
    if not material or material.name not in skin_names:
        continue
    center = poly.center
    side = "left_x" if center.x < -0.02 else "right_x" if center.x > 0.02 else None
    band = "thigh" if 0.45 <= center.z <= 0.90 else "calf" if 0.10 <= center.z < 0.45 else None
    if side is None or band is None:
        continue
    for loop_index in poly.loop_indices:
        uv = uv_layer.data[loop_index].uv
        regions[side][band].append([float(uv.x), float(uv.y)])

report = {}
for side, bands in regions.items():
    report[side] = {}
    for band, uvs in bands.items():
        report[side][band] = {
            "samples": len(uvs),
            "min": [min(uv[index] for uv in uvs) for index in range(2)] if uvs else None,
            "max": [max(uv[index] for uv in uvs) for index in range(2)] if uvs else None,
            "average": [sum(uv[index] for uv in uvs) / len(uvs) for index in range(2)] if uvs else None,
        }
print(json.dumps(report, indent=2))
