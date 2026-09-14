import bpy
from mathutils import Vector

scene = bpy.context.scene
target = Vector((1.0, -7.0, 1.0))
old_cam = scene.camera
cam_data = bpy.data.cameras.new('CLOTH_REBUILD_FINAL_CLOSE_DATA')
cam = bpy.data.objects.new('CLOTH_REBUILD_FINAL_CLOSE', cam_data)
scene.collection.objects.link(cam)
cam.location = (2.65, -10.3, 1.18)
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 78
scene.camera = cam

old_render = (scene.render.engine, scene.render.resolution_percentage, scene.render.filepath)
cycles = scene.cycles if hasattr(scene, 'cycles') else None
old_samples = cycles.samples if cycles and scene.render.engine == 'CYCLES' else None
scene.render.resolution_percentage = 50
if old_samples is not None:
    cycles.samples = 16

for frame, tag in [(1, 'f001'), (80, 'f080'), (120, 'f120')]:
    scene.frame_set(frame)
    scene.render.filepath = r'D:\project\blender_learning\renders\cloth_final_close_%s.png' % tag
    bpy.ops.render.render(write_still=True)

scene.camera = old_cam
scene.render.engine, scene.render.resolution_percentage, scene.render.filepath = old_render
if old_samples is not None:
    cycles.samples = old_samples
bpy.data.objects.remove(cam, do_unlink=True)
bpy.data.cameras.remove(cam_data)
scene.frame_set(120)
print('FINAL_CLOSE_RENDER|frames=1,80,120')
