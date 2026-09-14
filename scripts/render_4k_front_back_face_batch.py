import bpy
import json
import os
from datetime import datetime
from mathutils import Vector


scene = bpy.context.scene
camera = scene.camera or bpy.data.objects.get("CAM_Cine")
character = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if camera is None:
    raise RuntimeError("No render camera found")
if character is None:
    raise RuntimeError("Character mesh not found")


def world_bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    return Vector(mins), Vector(maxs)


def aim_at(obj, target):
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (Vector(target) - obj.location).to_track_quat("-Z", "Y")


mins, maxs = world_bounds(character)
center = (mins + maxs) * 0.5
body_target = Vector((center.x, center.y, (mins.z + maxs.z) * 0.5))
face_target = Vector((center.x, center.y, mins.z + (maxs.z - mins.z) * 0.86))

batch_name = f"今汐_4K_front_back_face_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
batch_dir = os.path.join(r"D:\project\blender_learning\renders", batch_name)
os.makedirs(batch_dir, exist_ok=True)

old_scene = scene
old_camera = scene.camera
old_transform = (
    camera.location.copy(),
    camera.rotation_mode,
    camera.rotation_euler.copy(),
    camera.rotation_quaternion.copy(),
    camera.data.lens,
    camera.data.sensor_fit,
)
old_dof = (
    camera.data.dof.use_dof,
    camera.data.dof.focus_object,
    camera.data.dof.focus_distance,
    camera.data.dof.aperture_fstop,
)
lanterns = [bpy.data.objects.get(name) for name in ("Lantern_A", "Lantern_B", "Lantern_C")]
old_lantern_visibility = [(lantern, lantern.hide_render) for lantern in lanterns if lantern is not None]
old_render = (
    scene.render.resolution_x,
    scene.render.resolution_y,
    scene.render.resolution_percentage,
    scene.render.image_settings.file_format,
    scene.render.image_settings.color_mode,
    scene.render.filepath,
)

scene.camera = camera
scene.render.engine = "CYCLES"
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = min(scene.cycles.adaptive_threshold, 0.015)
scene.cycles.samples = max(scene.cycles.samples, 128)
camera.data.sensor_fit = "HORIZONTAL"
camera.data.dof.use_dof = False
for lantern in lanterns:
    if lantern is not None:
        lantern.hide_render = True

shots = [
    {
        "name": "01_front_full_4k",
        "location": Vector((center.x, center.y - 5.2, body_target.z)),
        "target": body_target,
        "lens": 55.0,
    },
    {
        "name": "02_back_full_4k",
        "location": Vector((center.x, center.y + 5.2, body_target.z)),
        "target": body_target,
        "lens": 55.0,
    },
    {
        "name": "03_face_front_4k",
        "location": Vector((center.x + 0.02, center.y - 1.95, face_target.z)),
        "target": face_target,
        "lens": 85.0,
    },
]

rendered = []
try:
    for shot in shots:
        camera.location = shot["location"]
        camera.data.lens = shot["lens"]
        aim_at(camera, shot["target"])
        output = os.path.join(batch_dir, f"{shot['name']}.png")
        scene.render.filepath = output
        bpy.ops.render.render(write_still=True)
        rendered.append({
            "name": shot["name"],
            "path": output,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "camera_location": list(camera.location),
            "camera_target": list(shot["target"]),
        })
finally:
    camera.location = old_transform[0]
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = old_transform[3]
    camera.rotation_mode = old_transform[1]
    if old_transform[1] != "QUATERNION":
        camera.rotation_euler = old_transform[2]
    camera.data.lens, camera.data.sensor_fit = old_transform[4], old_transform[5]
    camera.data.dof.use_dof, camera.data.dof.focus_object, camera.data.dof.focus_distance, camera.data.dof.aperture_fstop = old_dof
    for lantern, hide_render in old_lantern_visibility:
        lantern.hide_render = hide_render
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.image_settings.file_format, scene.render.image_settings.color_mode, scene.render.filepath = old_render
    scene.camera = old_camera

manifest = {
    "batch": batch_name,
    "scene": old_scene.name,
    "character": character.name,
    "resolution": [3840, 2160],
    "shots": rendered,
}
manifest_path = os.path.join(batch_dir, "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)

blend_path = os.path.join(batch_dir, "今汐_4K_front_back_face.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path, copy=True, check_existing=False)

print(json.dumps({"batch_dir": batch_dir, "manifest": manifest_path, "blend": blend_path, "shots": rendered}, ensure_ascii=False, indent=2))
