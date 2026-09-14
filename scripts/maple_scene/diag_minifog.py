import bpy
cam = bpy.data.objects.get('Camera')
print('cam clip:', cam.data.clip_start, cam.data.clip_end)

# mini dense fog cube right in front of camera
fm = bpy.data.materials['FogVol']
bpy.ops.mesh.primitive_cube_add(size=4, location=(0.5, -10, 1.5))
mini = bpy.context.object
mini.name = 'MiniFog'
mini.data.materials.append(fm)

s = bpy.context.scene
s.cycles.samples = 16
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 30
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_minifog.png'
bpy.ops.render.render(write_still=True)
print('DONE')
