import bpy, json
from collections import Counter, defaultdict

obj = bpy.data.objects['卡提希娅_mesh']
arm = bpy.data.objects['卡提希娅_arm']

bone_matches = []
for b in arm.pose.bones:
    low = b.name.lower()
    if any(k in b.name for k in ('首', '頭', '头', '胸', '上半身')) or any(k in low for k in ('neck', 'head', 'chest')):
        bone_matches.append(b.name)

mat_index = next(i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == 'Up_Skin')
counts = Counter()
z_ranges = defaultdict(lambda: [999.0, -999.0])

for poly in obj.data.polygons:
    if poly.material_index != mat_index:
        continue
    for vi in poly.vertices:
        v = obj.data.vertices[vi]
        for g in v.groups:
            if g.weight < 0.05:
                continue
            name = obj.vertex_groups[g.group].name
            counts[name] += 1
            z_ranges[name][0] = min(z_ranges[name][0], v.co.z)
            z_ranges[name][1] = max(z_ranges[name][1], v.co.z)

result = {
    'bone_matches': bone_matches,
    'material_index': mat_index,
    'top_weight_groups': [
        {'name': n, 'count': c, 'z_min': round(z_ranges[n][0], 4), 'z_max': round(z_ranges[n][1], 4)}
        for n, c in counts.most_common(30)
    ]
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
