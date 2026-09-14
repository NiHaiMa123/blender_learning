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
)
old_camera = scene.camera
lanterns = [bpy.data.objects.get(name) for name in ("Lantern_A", "Lantern_B", "Lantern_C")]
old_lanterns = [(obj, obj.hide_render) for obj in lanterns if obj is not None]


def aim_at(target):
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = (Vector(target) - camera.location).to_track_quat("-Z", "Y")


try:
    for obj, _ in old_lanterns:
        obj.hide_render = True
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.cycles.samples = max(scene.cycles.samples, 64)
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True

    shots = [
        ("01_front_full_1080p.png", Vector((0.024, -5.014, 0.802)), Vector((0.024, 0.186, 0.802)), 55.0, "HORIZONTAL"),
        ("02_right_leg_ring_1080p.png", Vector((0.0, -1.82, 0.72)), Vector((-0.02, 0.02, 0.72)), 85.0, "VERTICAL"),
    ]
    for filename, location, target, lens, sensor_fit in shots:
        camera.location = location
        camera.data.lens = lens
        camera.data.sensor_fit = sensor_fit
        aim_at(target)
        scene.render.filepath = os.path.join(preview_dir, filename)
        bpy.ops.render.render(write_still=True)
finally:
    camera.location = old_transform[0]
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = old_transform[3]
    camera.rotation_mode = old_transform[1]
    if old_transform[1] != "QUATERNION":
        camera.rotation_euler = old_transform[2]
    camera.data.lens, camera.data.sensor_fit = old_transform[4], old_transform[5]
    scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old_render
    scene.camera = old_camera
    for obj, hide_render in old_lanterns:
        obj.hide_render = hide_render

print(preview_dir)
