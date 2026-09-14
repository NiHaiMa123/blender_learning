import bpy
from collections import Counter, defaultdict

obj = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_mesh')
mat_names = [m.name if m else '' for m in obj.data.materials]
regions = {
    'skirt': {'外裙子', '外裙子前外', '外裙子内里', '外裙子2', '外裙子隐藏', '外裙子内侧', '纱内侧', '纱外侧'},
    'sleeve': {'袖子', '袖子2'},
    'ribbons': {'前带子', '后带子', '前带子两条'},
}
for region, wanted in regions.items():
    mids = {i for i, n in enumerate(mat_names) if n in wanted}
    polys = [p for p in obj.data.polygons if p.material_index in mids]
    vids = sorted(set(v for p in polys for v in p.vertices))
    print('REGION|%s|mids=%s|faces=%d|verts=%d' % (region, sorted(mids), len(polys), len(vids)))
    if not vids:
        continue
    zs = [obj.data.vertices[v].co.z for v in vids]
    print('  Z|%.4f..%.4f' % (min(zs), max(zs)))
    # Weighted group coverage for region vertices.
    group_w = defaultdict(float)
    group_n = Counter()
    for vi in vids:
        for g in obj.data.vertices[vi].groups:
            name = obj.vertex_groups[g.group].name
            group_w[name] += g.weight
            if g.weight > 0.05:
                group_n[name] += 1
    top = sorted(group_w.items(), key=lambda x: x[1], reverse=True)[:25]
    print('  GROUPS|' + ','.join('%s=%.1f/%d' % (n, w, group_n[n]) for n, w in top))
    # Top/bottom coordinate samples and group names for likely pin vertices.
    for label, chosen in [('TOP', sorted(vids, key=lambda v: obj.data.vertices[v].co.z, reverse=True)[:20]), ('BOTTOM', sorted(vids, key=lambda v: obj.data.vertices[v].co.z)[:10])]:
        vals = []
        for vi in chosen:
            gs = sorted([(obj.vertex_groups[g.group].name, round(g.weight, 2)) for g in obj.data.vertices[vi].groups], key=lambda x: -x[1])[:4]
            vals.append('%d:%.3f:%s' % (vi, obj.data.vertices[vi].co.z, '/'.join(n for n, w in gs)))
        print('  %s|%s' % (label, ';'.join(vals)))
