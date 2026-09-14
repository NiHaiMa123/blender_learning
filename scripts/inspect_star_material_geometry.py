import bpy, json
from collections import defaultdict, deque

obj = bpy.data.objects['卡提希娅_mesh']
index = next(i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == 'Star')
polys = [p for p in obj.data.polygons if p.material_index == index]
verts = sorted({v for p in polys for v in p.vertices})
coords = [obj.data.vertices[i].co for i in verts]

adj = defaultdict(set)
poly_by_vert = defaultdict(list)
for p in polys:
    for v in p.vertices:
        poly_by_vert[v].append(p.index)
for plist in poly_by_vert.values():
    for a in plist:
        adj[a].update(plist)

remaining = {p.index for p in polys}
components = []
while remaining:
    start = remaining.pop()
    queue = [start]
    comp = {start}
    while queue:
        cur = queue.pop()
        for nxt in adj[cur]:
            if nxt in remaining:
                remaining.remove(nxt)
                comp.add(nxt)
                queue.append(nxt)
    components.append(len(comp))

result = {
    'slot': index,
    'polygons': len(polys),
    'vertices': len(verts),
    'components': sorted(components, reverse=True),
    'bbox_min': [min(c[i] for c in coords) for i in range(3)],
    'bbox_max': [max(c[i] for c in coords) for i in range(3)],
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
