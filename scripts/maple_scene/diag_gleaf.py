import bpy, math
o = bpy.data.collections['LEAF_GROUND_SRC'].objects['gleaf_0']
o.location = (0.5, -11.0, 1.3)
o.rotation_euler = (math.radians(70), 0, 0)
o.scale = (4,4,4)
s = bpy.context.scene
s.cycles.samples = 24
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 25
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_gleaf.png'
bpy.ops.render.render(write_still=True)
o.location = (0, 0, -60)
o.scale = (1,1,1)
print('DONE')
