import bpy
fm = bpy.data.materials['FogVol']
nt = fm.node_tree
pv = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeVolumePrincipled')
for l in list(nt.links):
    if l.to_socket == pv.inputs['Density']:
        nt.links.remove(l)
pv.inputs['Density'].default_value = 0.02
s = bpy.context.scene
s.cycles.samples = 16
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 30
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_fogconst.png'
bpy.ops.render.render(write_still=True)
print('DONE')
