import bpy
import os
from mathutils import Vector

scene = bpy.context.scene
camera = scene.camera
old_transform = (
    camera.location.copy(),
    camera.rotation_mode,
    camera.rotation_euler.copy(),
    camera.rotation_quaternion.copy(),
    camera.data.lens,
    camera.data.sensor_fit,
)
old_render = (
    scene.render.engine,
    scene.render.resolution_x,
    scene.render.resolution_y,
    scene.render.resolution_percentage,
    scene.render.filepath,
)

target = Vector((-0.02, 0.02, 0.72))
camera.location = Vector((0.0, -1.82, 0.72))
camera.rotation_mode = "QUATERNION"
camera.rotation_quaternion = (target - camera.location).to_track_quat("-Z", "Y")
camera.data.lens = 85.0
camera.data.sensor_fit = "VERTICAL"

output = r"C:\Users\Administrator\AppData\Local\Temp\opencode\今汐_leg_ring_diagnostic.png"
os.makedirs(os.path.dirname(output), exist_ok=True)
scene.render.engine = "CYCLES"
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.filepath = output
scene.cycles.samples = max(scene.cycles.samples, 96)
scene.cycles.use_denoising = True
bpy.ops.render.render(write_still=True)

camera.location = old_transform[0]
camera.rotation_mode = "QUATERNION"
camera.rotation_quaternion = old_transform[3]
camera.rotation_mode = old_transform[1]
if old_transform[1] != "QUATERNION":
    camera.rotation_euler = old_transform[2]
camera.data.lens, camera.data.sensor_fit = old_transform[4], old_transform[5]
scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old_render
print(output)
