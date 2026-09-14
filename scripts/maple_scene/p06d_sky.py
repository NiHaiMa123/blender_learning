exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
w = scene.world
nt = w.node_tree

# ---------- blue gradient sky: horizon pale -> zenith deep blue ----------
sky = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexSky'), None)
if sky:
    nt.nodes.remove(sky)
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
for l in list(nt.links):
    if l.to_node == bg:
        nt.links.remove(l)

tc = nt.nodes.new('ShaderNodeTexCoord')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
mpr = nt.nodes.new('ShaderNodeMapRange')
mpr.inputs['From Min'].default_value = -0.05
mpr.inputs['From Max'].default_value = 0.55
mpr.inputs['To Min'].default_value = 0.0
mpr.inputs['To Max'].default_value = 1.0
mpr.clamp = True
ramp = nt.nodes.new('ShaderNodeValToRGB')
cr = ramp.color_ramp
cr.elements[0].color = (0.62, 0.72, 0.88, 1)   # horizon haze
cr.elements[0].position = 0.0
e = cr.elements.new(0.45); e.color = (0.30, 0.5, 0.82, 1)
cr.elements[1].color = (0.12, 0.3, 0.7, 1)     # zenith
cr.elements[1].position = 1.0
nt.links.new(tc.outputs['Normal'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Z'], mpr.inputs['Value'])
nt.links.new(mpr.outputs['Result'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 0.6

# ---------- birch puffs hug branch tips ----------
be = bpy.data.objects.get('BirchEmitter')
if be:
    bpy.data.objects.remove(be, do_unlink=True)
can_col = col('CANOPY')
gn = bpy.data.node_groups['GN_Canopy']
tips = [((8.3, 3.5, 6.0), 0.75), ((10.0, 3.5, 7.4), 0.7), ((8.4, 3.6, 8.4), 0.7),
        ((9.7, 3.7, 9.3), 0.65), ((8.9, 3.8, 9.5), 0.6)]
bpuffs = []
for c, r in tips:
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=1, location=c)
    p = bpy.context.object; p.scale.z = 0.7
    bpy.ops.object.transform_apply(scale=True)
    for uc in list(p.users_collection):
        uc.objects.unlink(p)
    can_col.objects.link(p)
    bpuffs.append(p)
bpy.ops.object.select_all(action='DESELECT')
for p in bpuffs:
    p.select_set(True)
bpy.context.view_layer.objects.active = bpuffs[0]
bpy.ops.object.join()
be = bpy.context.object; be.name = 'BirchEmitter'
m2 = be.modifiers.new('leafscatter', 'NODES'); m2.node_group = gn

save()
render_preview('p06d_sky_eevee.png', pct=50)
