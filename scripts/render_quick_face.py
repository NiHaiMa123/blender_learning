import bpy
import os
from mathutils import Vector

scene = bpy.context.scene
camera = scene.camera
preview_dir = r"D:\project\blender_learning\renders\_preview_right_leg_uv_1080p"
os.makedirs(preview_dir, exist_ok=True)

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
    scene.cycles.samples,
    scene.cycles.use_denoising,
    scene.cycles.use_adaptive_sampling,
)
old_camera = scene.camera


def aim_at(target):
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = (Vector(target) - camera.location).to_track_quat("-Z", "Y")


try:
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 40
    scene.render.image_settings.file_format = "PNG"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True

    camera.location = Vector((0.044, -1.764, 1.379))
    camera.data.lens = 85.0
    camera.data.sensor_fit = "HORIZONTAL"
    aim_at(Vector((0.024, 0.186, 1.379)))
    scene.render.filepath = os.path.join(preview_dir, "quick_face_skin.png")
    bpy.ops.render.render(write_still=True)
finally:
    camera.location = old_transform[0]
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = old_transform[3]
    camera.rotation_mode = old_transform[1]
    if old_transform[1] != "QUATERNION":
        camera.rotation_euler = old_transform[2]
    camera.data.lens, camera.data.sensor_fit = old_transform[4], old_transform[5]
    (scene.render.engine, scene.render.resolution_x, scene.render.resolution_y,
     scene.render.resolution_percentage, scene.render.filepath,
     scene.cycles.samples, scene.cycles.use_denoising,
     scene.cycles.use_adaptive_sampling) = old_render
    scene.camera = old_camera

print("quick face done")
