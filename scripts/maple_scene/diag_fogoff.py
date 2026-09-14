import bpy
fog = bpy.data.objects['FogCube']
fog.hide_render = True
s = bpy.context.scene
s.cycles.samples = 32
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 40
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_fogoff.png'
bpy.ops.render.render(write_still=True)
fog.hide_render = False
print('DONE')
