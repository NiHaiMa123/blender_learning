import bpy
from mathutils import Vector

scene = bpy.context.scene
old_camera = scene.camera
camera_data = bpy.data.cameras.new('CLOTH_REBUILD_REAR_PREVIEW_DATA')
camera = bpy.data.objects.new('CLOTH_REBUILD_REAR_PREVIEW', camera_data)
scene.collection.objects.link(camera)

target = Vector((1.0, -7.0, 0.76))
# Opposite side of the front three-quarter validation camera.
camera.location = (-0.9, -3.2, 0.96)
camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.lens = 72
scene.camera = camera

render = scene.render
old_render = (render.resolution_percentage, render.filepath)
cycles = scene.cycles if hasattr(scene, 'cycles') else None
old_samples = cycles.samples if cycles and render.engine == 'CYCLES' else None
render.resolution_percentage = 40
if old_samples is not None:
    cycles.samples = 12

for frame, tag in ((1, 'f001'), (80, 'f080')):
    scene.frame_set(frame)
    render.filepath = (
        r'D:\project\blender_learning\renders\cloth_rear_v7_' + tag + '.png'
    )
    bpy.ops.render.render(write_still=True)

scene.camera = old_camera
render.resolution_percentage, render.filepath = old_render
if old_samples is not None:
    cycles.samples = old_samples
bpy.data.objects.remove(camera, do_unlink=True)
bpy.data.cameras.remove(camera_data)
scene.frame_set(80)
print('REAR_PREVIEW_V7|frames=1,80')
