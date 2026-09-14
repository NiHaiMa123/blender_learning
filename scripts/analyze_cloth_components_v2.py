import bpy
from collections import defaultdict, deque

obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mesh = obj.data
adj = defaultdict(set)
for edge in mesh.edges:
    a, b = edge.vertices
    adj[a].add(b)
    adj[b].add(a)
seen = set()
components = []
for start in range(len(mesh.vertices)):
    if start in seen:
        continue
    q = deque([start])
    seen.add(start)
    comp = []
    while q:
        v = q.popleft()
        comp.append(v)
        for n in adj[v]:
            if n not in seen:
                seen.add(n)
                q.append(n)
    components.append(comp)
components.sort(key=len, reverse=True)
print('COMPONENTS|%d' % len(components))
for i, comp in enumerate(components[:40]):
    zs = [mesh.vertices[v].co.z for v in comp]
    top = max(zs)
    pin = sum(1 for z in zs if z >= top - 0.08)
    print('COMP|%03d|verts=%d|z=%.3f..%.3f|pin08=%d' % (i, len(comp), min(zs), max(zs), pin))
