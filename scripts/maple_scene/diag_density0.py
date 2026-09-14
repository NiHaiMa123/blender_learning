import bpy
ng = bpy.data.node_groups['GN_Carpet']
dist = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces'][0]
dist.inputs['Density'].default_value = 0.0
s = bpy.context.scene
s.cycles.samples = 16
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 25
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_density0.png'
bpy.ops.render.render(write_still=True)
dist.inputs['Density'].default_value = 15.0
print('DONE')
