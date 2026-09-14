import bpy
import json
from collections import defaultdict, deque
from mathutils import Vector

TARGETS = {"外裙子", "外裙子2", "外裙子前外", "外裙子内侧", "外裙子内里", "前带子", "前带子两条", "袖子", "袖子2", "鞋子", "头饰"}
obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")

rows = []
for slot_index, slot in enumerate(obj.material_slots):
    material = slot.material
    if not material or material.name not in TARGETS:
        continue
    polygons = [poly for poly in obj.data.polygons if poly.material_index == slot_index]
    vertex_to_faces = defaultdict(list)
    for local_index, poly in enumerate(polygons):
        for vertex_index in poly.vertices:
            vertex_to_faces[vertex_index].append(local_index)
    seen = set()
    components = []
    for start in range(len(polygons)):
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for vertex_index in polygons[current].vertices:
                for neighbor in vertex_to_faces[vertex_index]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
        points = [obj.data.vertices[vertex_index].co for face_index in component for vertex_index in polygons[face_index].vertices]
        mins = [min(point[index] for point in points) for index in range(3)]
        maxs = [max(point[index] for point in points) for index in range(3)]
        dimensions = tuple(round(maxs[index] - mins[index], 3) for index in range(3))
        center = tuple(round((maxs[index] + mins[index]) * 0.5, 3) for index in range(3))
        components.append({"polygons": len(component), "center": center, "size": dimensions})
    components.sort(key=lambda item: item["polygons"], reverse=True)
    rows.append({"material": material.name, "components": components[:20], "component_count": len(components)})

print(json.dumps(rows, ensure_ascii=False, indent=2))
