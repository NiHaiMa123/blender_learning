import bpy
ng = bpy.data.node_groups['GN_Carpet']
coll = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeCollectionInfo'][0]
coll.inputs['Collection'].default_value = bpy.data.collections['LEAF_SRC']
s = bpy.context.scene
s.cycles.samples = 16
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 30
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_swap.png'
bpy.ops.render.render(write_still=True)
print('DONE')
