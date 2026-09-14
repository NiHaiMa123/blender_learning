import bpy
import os
from mathutils import Vector

scene = bpy.context.scene
cam = scene.camera
old_cam = (cam.location.copy(), cam.rotation_euler.copy(), cam.data.lens, cam.data.sensor_fit)
old_render = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath)
target = Vector((0.0, 0.0, 1.24))
cam.location = Vector((0.35, -1.05, 1.32))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 85
cam.data.sensor_fit = "VERTICAL"
output = r"D:\project\blender_learning\renders\今汐_after_material_closeup.png"
os.makedirs(os.path.dirname(output), exist_ok=True)
scene.render.resolution_x = 720
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = output
bpy.ops.render.render(write_still=True)
cam.location, cam.rotation_euler, cam.data.lens, cam.data.sensor_fit = old_cam
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old_render
print(output)
