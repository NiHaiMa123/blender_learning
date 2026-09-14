exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

# 1) remove leftover leaf test objects
lt = bpy.data.collections.get('LEAF_TEST')
if lt:
    for o in list(lt.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(lt)

# 2) leaf ramp: deeper reds, less amber
m = bpy.data.materials['MapleLeaf']
ramp = [n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeValToRGB'][0]
cr = ramp.color_ramp
cols = [(0.0, (0.20, 0.006, 0.01, 1)),
        (0.30, (0.48, 0.02, 0.012, 1)),
        (0.55, (0.66, 0.06, 0.015, 1)),
        (0.78, (0.78, 0.15, 0.02, 1)),
        (1.0, (0.88, 0.30, 0.05, 1))]
while len(cr.elements) > 1:
    cr.elements.remove(cr.elements[-1])
cr.elements[0].position, cr.elements[0].color = cols[0]
for pos, c in cols[1:]:
    e = cr.elements.new(pos); e.color = c

# 3) rebuild canopy emitter: bigger/denser/more coverage
em = bpy.data.objects.get('CanopyEmitter')
if em:
    bpy.data.objects.remove(em, do_unlink=True)
can_col = col('CANOPY')

puff_specs = [
    # upper-left mass, exits frame
    ((-5.9, 0.4, 8.2), 1.7, 0.75),
    ((-5.0, 0.2, 7.5), 1.5, 0.7),
    ((-6.8, 0.5, 9.0), 1.6, 0.8),
    ((-7.6, 0.6, 9.8), 1.5, 0.85),
    ((-6.2, 0.3, 9.7), 1.4, 0.8),
    # top band along limb B -> right
    ((-2.9, 0.0, 6.9), 1.6, 0.7),
    ((-1.2, 0.3, 7.5), 1.8, 0.7),
    ((0.6, 0.4, 7.9), 1.8, 0.7),
    ((2.4, 0.5, 8.1), 1.7, 0.7),
    ((4.2, 0.6, 8.3), 1.6, 0.7),
    ((5.7, 0.6, 8.4), 1.3, 0.7),
    # second top layer for thickness
    ((-4.2, 0.5, 8.7), 1.6, 0.8),
    ((-2.4, 0.6, 8.6), 1.6, 0.8),
    ((-0.4, 0.7, 8.9), 1.7, 0.8),
    ((1.6, 0.8, 9.2), 1.6, 0.8),
    ((3.6, 0.9, 9.3), 1.5, 0.8),
    ((5.0, 0.9, 9.2), 1.3, 0.75),
    # center fork fill
    ((-2.7, -0.4, 8.2), 1.4, 0.75),
    ((-3.4, 0.6, 7.8), 1.3, 0.7),
    # lower hanging clusters
    ((-1.6, -1.3, 5.4), 1.1, 0.8),
    ((-2.5, -0.9, 5.6), 0.9, 0.8),
    ((0.2, -0.6, 6.3), 1.0, 0.75),   # low cluster right of center
    ((4.9, 0.3, 6.9), 1.0, 0.75),   # right-edge spill-down
    # rear depth
    ((-2.4, 1.8, 7.6), 1.3, 0.7),
    ((-3.1, 2.2, 8.0), 1.1, 0.7),
    ((0.8, 1.9, 8.5), 1.3, 0.7),
]
puffs = []
for i, (c, r, sz) in enumerate(puff_specs):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=2, location=c)
    p = bpy.context.object
    p.name = f'puff{i:02d}'
    p.scale.z = sz
    p.scale.y *= 0.85
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for uc in list(p.users_collection):
        uc.objects.unlink(p)
    can_col.objects.link(p)
    puffs.append(p)

bpy.ops.object.select_all(action='DESELECT')
for p in puffs:
    p.select_set(True)
bpy.context.view_layer.objects.active = puffs[0]
bpy.ops.object.join()
emitter = bpy.context.object
emitter.name = 'CanopyEmitter'
emitter.display_type = 'WIRE'

gn = bpy.data.node_groups.get('GN_Canopy')
# bump density
for n in gn.nodes:
    if n.bl_idname == 'GeometryNodeDistributePointsOnFaces':
        n.inputs['Density'].default_value = 340.0
mod = emitter.modifiers.new('leafscatter', 'NODES')
mod.node_group = gn

save()
render_preview('p03c_canopy_eevee.png', pct=50)
