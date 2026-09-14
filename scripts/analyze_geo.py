"""Analyze leaf-card GEOMETRY of the lakeside asset trees.
For each foliage mesh: count disconnected islands, verts/faces per island,
planarity (flat vs bent), island bounding-box size distribution."""
import bpy, bmesh, json, sys
import numpy as np

def islands(obj):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    # tag islands via flood fill on verts
    seen = np.zeros(len(bm.verts), dtype=bool)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    result = []
    adj = {}
    # build vert->verts adjacency from edges
    for e in bm.edges:
        a, b = e.verts[0].index, e.verts[1].index
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    import collections
    for v in bm.verts:
        if seen[v.index]:
            continue
        q = collections.deque([v.index])
        seen[v.index] = True
        comp = []
        while q:
            i = q.popleft()
            comp.append(i)
            for j in adj.get(i, ()):  # noqa
                if not seen[j]:
                    seen[j] = True
                    q.append(j)
        result.append(comp)
    bm.free()
    return result

def analyze(name, sample_islands=400):
    o = bpy.data.objects.get(name)
    if not o:
        return None
    me = o.data
    comps = islands(o)
    sizes = [len(c) for c in comps]
    # per-island planarity on a sample: fit plane via SVD, measure residual/bbox
    planarity = []
    cardinfo = []
    rng = np.random.default_rng(0)
    idxs = rng.choice(len(comps), min(sample_islands, len(comps)), replace=False)
    verts = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get('co', verts)
    verts = verts.reshape(-1, 3)
    for ci in idxs:
        pts = verts[np.array(comps[ci])]
        ctr = pts.mean(0)
        u, s, vt = np.linalg.svd(pts - ctr, full_matrices=False)
        ext = pts.max(0) - pts.min(0)
        thickness_ratio = float(s[2] / s[0]) if len(s) > 2 and s[0] > 0 else 0.0
        planarity.append(thickness_ratio)
        cardinfo.append({'verts': len(pts), 'extent': [round(float(x), 3) for x in ext],
                         'flat_ratio': round(thickness_ratio, 4)})
    return {
        'name': name, 'verts': len(me.vertices), 'faces': len(me.polygons),
        'islands': len(comps),
        'verts_per_island': {'min': int(min(sizes)), 'max': int(max(sizes)),
                             'mean': round(float(np.mean(sizes)), 1),
                             'median': int(np.median(sizes))},
        'flat_ratio_mean': round(float(np.mean(planarity)), 4),
        'flat_ratio_p10': round(float(np.percentile(planarity, 10)), 4),
        'flat_ratio_p90': round(float(np.percentile(planarity, 90)), 4),
        'sample': cardinfo[:8],
    }

out = {}
for name in ['cgaxis_models_05_15_obj']:
    try:
        out[name] = analyze(name)
        print(name, 'OK')
    except Exception as e:
        out[name] = 'ERR ' + str(e)
        print(name, 'ERR', e)

with open(r'D:/project/blender_learning/scripts/geo_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('GEOJSON DONE')
