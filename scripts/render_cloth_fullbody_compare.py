import bpy
scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
cam = bpy.data.objects.get('Camera')
if cam is None:
    raise RuntimeError('Camera not found')
old_cam = scene.camera
old = (scene.render.engine, scene.render.resolution_percentage, scene.render.filepath)
cycles = scene.cycles if hasattr(scene, 'cycles') else None
old_samples = cycles.samples if cycles and scene.render.engine == 'CYCLES' else None
scene.camera = cam
scene.render.resolution_percentage = 50
if old_samples is not None:
    cycles.samples = 16
for f, tag in [(1, 'f001'), (40, 'f040')]:
    scene.frame_set(f)
    scene.render.filepath = r'D:\project\blender_learning\renders\cloth_fullbody_stable_%s.png' % tag
    bpy.ops.render.render(write_still=True)
scene.camera = old_cam
scene.render.engine, scene.render.resolution_percentage, scene.render.filepath = old
if old_samples is not None:
    cycles.samples = old_samples
scene.frame_set(40)
print('DONE')
