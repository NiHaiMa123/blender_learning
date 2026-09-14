exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

# ---------- carpet-specific leaf material: matte, darker, less translucent ----------
m = bpy.data.materials.get('MapleLeafGround') or bpy.data.materials.new('MapleLeafGround')
m.use_nodes = True
nt = m.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
mix = nt.nodes.new('ShaderNodeMixShader')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
transl = nt.nodes.new('ShaderNodeBsdfTranslucent')
oi = nt.nodes.new('ShaderNodeObjectInfo')
ramp = nt.nodes.new('ShaderNodeValToRGB')
cr = ramp.color_ramp
cr.elements.remove(cr.elements[1])
e0 = cr.elements[0]; e0.position = 0.0; e0.color = (0.07, 0.004, 0.004, 1)
for pos, c in [(0.3, (0.22, 0.012, 0.006, 1)),
               (0.55, (0.42, 0.03, 0.008, 1)),
               (0.78, (0.6, 0.08, 0.012, 1)),
               (1.0, (0.72, 0.2, 0.03, 1))]:
    e = cr.elements.new(pos); e.color = c
bsdf.inputs['Roughness'].default_value = 0.85
if 'Specular IOR Level' in bsdf.inputs:
    bsdf.inputs['Specular IOR Level'].default_value = 0.25
transl.inputs['Color'].default_value = (0.3, 0.02, 0.01, 1)
mix.inputs[0].default_value = 0.12
nt.links.new(oi.outputs['Random'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
nt.links.new(transl.outputs['BSDF'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])

# ---------- LEAF_GROUND_SRC collection ----------
gsrc = col('LEAF_GROUND_SRC')
for o in list(gsrc.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for i, src_name in enumerate(('leaf_A', 'leaf_B', 'leaf_C')):
    so = bpy.data.objects.get(src_name)
    d = so.copy()  # shares mesh
    d.name = f'gleaf_{i}'
    d.data = so.data.copy()  # own mesh for own material slots
    d.data.materials.clear()
    d.data.materials.append(m)
    d.location = (0, 0, -60)
    gsrc.objects.link(d)

# ---------- repoint carpet GN to ground leaves, restore distance density ----------
ng = bpy.data.node_groups['GN_Carpet']
coll = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeCollectionInfo'][0]
coll.inputs['Collection'].default_value = gsrc
dist = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces'][0]
mpr = [n for n in ng.nodes if n.bl_idname == 'ShaderNodeMapRange'][0]
dist.distribute_method = 'RANDOM'
ng.links.new(mpr.outputs['Result'], dist.inputs['Density'])
rot = [n for n in ng.nodes if n.bl_idname == 'FunctionNodeRandomValue' and n.data_type == 'FLOAT_VECTOR'][0]
rot.inputs['Min'].default_value = (-0.55, -0.55, -math.pi)
rot.inputs['Max'].default_value = (0.55, 0.55, math.pi)

save()
render_preview('p04c_carpet_eevee.png', pct=50)
