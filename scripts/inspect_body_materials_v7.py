import bpy
import json
from collections import Counter, defaultdict

obj = bpy.data.objects['CLOTH_REBUILD_BODY_STATIC']
mesh = obj.data
face_counts = Counter(face.material_index for face in mesh.polygons)
vertex_sets = defaultdict(set)
for face in mesh.polygons:
    vertex_sets[face.material_index].update(face.vertices)

items = []
for material_index, face_count in face_counts.most_common():
    name = mesh.materials[material_index].name if mesh.materials[material_index] else ''
    indices = vertex_sets[material_index]
    coords = [mesh.vertices[index].co for index in indices]
    items.append({
        'index': material_index,
        'name': name,
        'faces': face_count,
        'vertices': len(indices),
        'min': [round(min(co[axis] for co in coords), 4) for axis in range(3)],
        'max': [round(max(co[axis] for co in coords), 4) for axis in range(3)],
    })

print('BODY_MATERIALS_V7|' + json.dumps(items, ensure_ascii=False))
