"""Upgrade CardLeaf to V-folded 6-vert card (asset-proven shape) +
add a 3-card crossed cluster variant mixed into the scatter."""
import bpy, math, sys
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, move_to_col, save, render_preview

CARD_COLL = 'LEAF_CARD_SRC'
w, h = 0.66, 1.0
fold = math.radians(22)          # V-fold angle, asset ~14% thickness ratio
fy = (w / 2) * math.tan(fold)    # side verts pushed back along Y

# ---------- rebuild CardLeaf mesh as folded card ----------
me = bpy.data.objects['CardLeaf'].data
me.clear_geometry()
# 6 verts: left-top, left-bot, spine-top, spine-bot, right-top, right-bot
verts = [(-w/2, fy,  h/2), (-w/2, fy, -h/2),
         (0,    0,   h/2), (0,    0,  -h/2),
         (w/2,  fy,  h/2), (w/2,  fy, -h/2)]
faces = [(0, 1, 3, 2), (2, 3, 5, 4)]
me.from_pydata(verts, [], faces)
me.update()
# UV: each half maps to its half of the texture
uvl = me.uv_layers.active or me.uv_layers.new(name='UVMap')
uv_map = {0: (0.0, 1.0), 1: (0.0, 0.0), 2: (0.5, 1.0), 3: (0.5, 0.0),
          4: (1.0, 1.0), 5: (1.0, 0.0)}
for i, loop in enumerate(me.loops):
    uvl.data[i].uv = uv_map[loop.vertex_index]

# ---------- crossed cluster variant: 3 folded cards at 60deg ----------
me2 = bpy.data.meshes.get('CardClusterMesh') or bpy.data.meshes.new('CardClusterMesh')
if not me2.vertices:
    vs, fs, uvs = [], [], []
    for k in range(3):
        a = math.radians(60 * k)
        ca, sa = math.cos(a), math.sin(a)
        base = len(vs)
        for vx, vy, vz in verts:
            # rotate each card around Z, shrink slightly, stagger height
            vs.append((vx * ca - vy * sa, vx * sa + vy * ca, vz * 0.9 + 0.05 * k))
        fs += [(base+0, base+1, base+3, base+2), (base+2, base+3, base+5, base+4)]
    me2.from_pydata(vs, [], fs)
    me2.update()
    uvl2 = me2.uv_layers.new(name='UVMap')
    for i, loop in enumerate(me2.loops):
        uvl2.data[i].uv = uv_map[loop.vertex_index % 6]

mat = bpy.data.materials['MapleCard']
if not me2.materials:
    me2.materials.append(mat)

cluster = bpy.data.objects.get('CardCluster') or bpy.data.objects.new('CardCluster', me2)
if not cluster.users_collection:
    col(CARD_COLL).objects.link(cluster)
cluster.hide_render = True

# ---------- GN: mix card + cluster via collection info pick ----------
g = bpy.data.node_groups['GN_CardCanopy']
# replace ObjectInfo with CollectionInfo on LEAF_CARD_SRC for pick-instance variety
for n in list(g.nodes):
    if n.bl_idname == 'GeometryNodeObjectInfo':
        g.nodes.remove(n)
ci = g.nodes.new('GeometryNodeCollectionInfo')
ci.location = (-250, -200)
ci.inputs['Collection'].default_value = bpy.data.collections[CARD_COLL]
if ci.inputs.get('Separate Children'):
    ci.inputs['Separate Children'].default_value = True
if ci.inputs.get('Reset Children'):
    ci.inputs['Reset Children'].default_value = True
ip = next(n for n in g.nodes if n.bl_idname == 'GeometryNodeInstanceOnPoints')
ip.inputs['Pick Instance'].default_value = True
# unlink old instance link then wire collection instances
for l in list(g.links):
    if l.to_node == ip and l.to_socket.name == 'Instance':
        g.links.remove(l)
g.links.new(ci.outputs['Instances'], ip.inputs['Instance'])

# slightly lower density since cluster cards are denser-looking
dp = next(n for n in g.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces')
if dp.inputs.get('Density Max'):
    dp.inputs['Density Max'].default_value = 7.0

save()
render_preview('p09d_fold_eevee.png', pct=50)
print('FOLD DONE')
