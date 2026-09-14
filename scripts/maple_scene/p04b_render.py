import bpy
s = bpy.context.scene
s.cycles.samples = 32
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 35
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/p04_carpet_cycles.png'
bpy.ops.render.render(write_still=True)
print('DONE')
