import bpy
import json
from collections import defaultdict

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")

target_names = {"皮肤", "Codex Skin Right Leg Lift", "metal leg", "Codex Shoe Heel Metal"}
rows = []
for slot_index, slot in enumerate(obj.material_slots):
    material = slot.material
    if not material or material.name not in target_names:
        continue
    groups = defaultdict(list)
    for poly in obj.data.polygons:
        if poly.material_index != slot_index:
            continue
        center = poly.center
        side = "left_x" if center.x < -0.02 else "right_x" if center.x > 0.02 else "center"
        groups[side].append((center.x, center.y, center.z))
    row = {"slot": slot_index, "material": material.name, "groups": {}}
    for side, points in groups.items():
        row["groups"][side] = {
            "faces": len(points),
            "min": [min(point[index] for point in points) for index in range(3)],
            "max": [max(point[index] for point in points) for index in range(3)],
        }
    rows.append(row)

print(json.dumps(rows, ensure_ascii=False, indent=2))
