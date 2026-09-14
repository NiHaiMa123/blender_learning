import bpy, os
from mathutils import Vector

scene = bpy.data.scenes['Codex_Cycles_Render']
cam = scene.camera
bpy.context.window.scene = scene

location = Vector((0.30, -6.00, 0.93))
target = Vector((-0.03, 0.00, 0.86))
cam.location = location
cam.rotation_euler = (target - location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 78
cam.data.sensor_fit = 'VERTICAL'
cam.data.shift_x = 0.0
cam.data.shift_y = 0.0

scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.015
scene.render.resolution_x = 1080
scene.render.resolution_y = 1620
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

output = r'D:\project\blender_learning\renders\carthya_pose_reference_camera.png'
blend_copy = r'D:\project\blender_learning\renders\carthya_pose_reference_camera.blend'
os.makedirs(os.path.dirname(output), exist_ok=True)
scene.render.filepath = output
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=blend_copy, copy=True, check_existing=False)

print(output)
print(blend_copy)
return_value = {'render': output, 'blend': blend_copy}
