exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
w = scene.world
nt = w.node_tree

# 1) bluer sky: higher sun, slightly stronger
sky = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexSky')
sky.sun_elevation = math.radians(30)
sky.sun_rotation = math.radians(90)
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
bg.inputs['Strength'].default_value = 0.55

# 2) birch: darker bark + in-frame foliage puffs
bm = bpy.data.materials['BirchBark']
bb = next(n for n in bm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
bb.inputs['Base Color'].default_value = (0.28, 0.28, 0.27, 1)

can_col = col('CANOPY')
gn = bpy.data.node_groups['GN_Canopy']
bpuffs = []
for i, (c, r) in enumerate([((8.5, 3.5, 6.4), 0.8), ((9.7, 3.6, 7.2), 0.7), ((8.8, 3.6, 7.6), 0.65)]):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=1, location=c)
    p = bpy.context.object; p.scale.z = 0.75
    bpy.ops.object.transform_apply(scale=True)
    for uc in list(p.users_collection):
        uc.objects.unlink(p)
    can_col.objects.link(p)
    bpuffs.append(p)
be = bpy.data.objects.get('BirchEmitter')
if be:
    bpy.ops.object.select_all(action='DESELECT')
    for p in bpuffs:
        p.select_set(True)
    be.select_set(True)
    bpy.context.view_layer.objects.active = be
    bpy.ops.object.join()

# 3) deeper crimson carpet
gm = bpy.data.materials['MapleLeafGround']
ramp = next(n for n in gm.node_tree.nodes if n.bl_idname == 'ShaderNodeValToRGB')
cr = ramp.color_ramp
cols = [(0.0, (0.06, 0.003, 0.003, 1)),
        (0.3, (0.18, 0.008, 0.004, 1)),
        (0.55, (0.35, 0.02, 0.006, 1)),
        (0.78, (0.52, 0.055, 0.01, 1)),
        (1.0, (0.62, 0.14, 0.02, 1))]
while len(cr.elements) > 1:
    cr.elements.remove(cr.elements[-1])
cr.elements[0].position, cr.elements[0].color = cols[0]
for pos, c in cols[1:]:
    e = cr.elements.new(pos); e.color = c

# 4) grass slightly more saturated
grm = bpy.data.materials['Grass']
gb = next(n for n in grm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
gb.inputs['Base Color'].default_value = (0.075, 0.19, 0.028, 1)

save()
render_preview('p06c_tune_eevee.png', pct=50)
