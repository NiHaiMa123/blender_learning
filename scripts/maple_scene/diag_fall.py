import bpy
em = bpy.data.objects['FallEmitter']
ng = bpy.data.node_groups['GN_Falling']
# crank density way up for visibility test
dist = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsInVolume')
dist.inputs['Density'].default_value = 0.6
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.render.resolution_percentage = 50
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_fall_dense.png'
bpy.ops.render.render(write_still=True)
print('DONE')
