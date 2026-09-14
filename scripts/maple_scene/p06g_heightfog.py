exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

fm = bpy.data.materials['FogVol']
nt = fm.node_tree
pv = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeVolumePrincipled')

geo = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeNewGeometry'), None) or nt.nodes.new('ShaderNodeNewGeometry')
sep = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeSeparateXYZ'), None) or nt.nodes.new('ShaderNodeSeparateXYZ')
mpr = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange'), None) or nt.nodes.new('ShaderNodeMapRange')
mul = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeMath'), None) or nt.nodes.new('ShaderNodeMath')

mpr.inputs['From Min'].default_value = -2.0    # dense near ground
mpr.inputs['From Max'].default_value = 30.0    # gone by z=30
mpr.inputs['To Min'].default_value = 1.0
mpr.inputs['To Max'].default_value = 0.0
mpr.clamp = True
mul.operation = 'MULTIPLY'
mul.inputs[1].default_value = 0.05             # peak density at z=0
nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Z'], mpr.inputs['Value'])
nt.links.new(mpr.outputs['Result'], mul.inputs[0])
for l in list(nt.links):
    if l.to_socket == pv.inputs['Density']:
        nt.links.remove(l)
nt.links.new(mul.outputs['Value'], pv.inputs['Density'])
pv.inputs['Color'].default_value = (0.55, 0.63, 0.78, 1)

save()
bpy.context.scene.cycles.samples = 64
render_preview('p06g_heightfog_cycles.png', engine='CYCLES', pct=50)
