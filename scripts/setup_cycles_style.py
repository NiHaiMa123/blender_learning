import bpy
import math
from mathutils import Vector

SOURCE_SCENE = "Scene"
RENDER_SCENE = "Codex_Cycles_Render"
TAG = "codex_cycles_style"


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def make_light(scene, name, light_type, location, energy, color, size=1.0, target=None):
    data = bpy.data.lights.new(name=f"{name}_Data", type=light_type)
    data.energy = energy
    data.color = color
    if light_type == "AREA":
        data.shape = "DISK"
        data.size = size
    elif light_type == "POINT":
        data.shadow_soft_size = size
    obj = bpy.data.objects.new(name, data)
    obj[TAG] = True
    scene.collection.objects.link(obj)
    obj.location = location
    if target is not None:
        point_at(obj, target)
    return obj


src = bpy.data.scenes.get(SOURCE_SCENE) or bpy.context.scene
old_render = bpy.data.scenes.get(RENDER_SCENE)
if old_render:
    bpy.data.scenes.remove(old_render)

scene = bpy.data.scenes.new(RENDER_SCENE)

# Share the finished character and living-room geometry without duplicating the heavy scene.
for child in src.collection.children:
    scene.collection.children.link(child)
for obj in src.collection.objects:
    if obj.name not in scene.objects:
        scene.collection.objects.link(obj)

# Use a dedicated dark, cool world for the cinematic lighting pass.
scene.world = src.world.copy() if src.world else bpy.data.worlds.new("Codex_Cycles_World")
scene.world.name = "Codex_Cycles_World"
scene.world.use_nodes = True
world_nodes = scene.world.node_tree.nodes
background = world_nodes.get("Background")
if background:
    background.inputs["Color"].default_value = (0.012, 0.018, 0.035, 1.0)
    background.inputs["Strength"].default_value = 0.04

target = Vector((0.0, 0.05, 0.92))

# Camera: close full-body portrait, slight low angle and Dutch roll like the reference.
cam_data = bpy.data.cameras.new("Codex_Render_Camera_Data")
cam = bpy.data.objects.new("Codex_Render_Camera", cam_data)
cam[TAG] = True
scene.collection.objects.link(cam)
cam.location = (1.75, -5.05, 1.32)
point_at(cam, target)
cam.rotation_euler.rotate_axis("Z", math.radians(-6.5))
cam_data.lens = 58.0
cam_data.sensor_width = 36.0
cam_data.sensor_fit = "VERTICAL"
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 2.8

focus = bpy.data.objects.new("Codex_Focus", None)
focus[TAG] = True
focus.empty_display_type = "PLAIN_AXES"
focus.location = target
scene.collection.objects.link(focus)
cam_data.dof.focus_object = focus
scene.camera = cam

# Three-point lighting: warm soft key, cool fill, cyan-violet rim.
make_light(
    scene, "Codex_Key_Warm", "AREA", (-3.2, -3.8, 4.1),
    180.0, (1.0, 0.82, 0.68), 3.2, (0.0, 0.0, 0.95),
)
make_light(
    scene, "Codex_Fill_Cool", "AREA", (3.8, -2.6, 2.7),
    70.0, (0.34, 0.48, 1.0), 3.8, (0.0, 0.05, 1.0),
)
make_light(
    scene, "Codex_Rim_Cyan", "AREA", (-2.4, 2.2, 3.1),
    160.0, (0.18, 0.72, 1.0), 2.3, (0.0, 0.15, 1.15),
)
make_light(
    scene, "Codex_Practical_Warm", "POINT", (1.3, -0.45, 3.1),
    40.0, (1.0, 0.34, 0.12), 0.45,
)

# Keep the room's existing sun as a restrained warm ambient source.
sun = bpy.data.objects.get("Sun")
if sun and sun.type == "LIGHT":
    if "codex_original_energy" not in sun.data:
        sun.data["codex_original_energy"] = float(sun.data.energy)
        sun.data["codex_original_color"] = list(sun.data.color)
    sun.data.energy = 0.08
    sun.data.color = (1.0, 0.72, 0.5)

# Cycles and color management.
scene.render.engine = "CYCLES"
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.02
scene.cycles.max_bounces = 8
scene.cycles.diffuse_bounces = 4
scene.cycles.glossy_bounces = 4
scene.cycles.transmission_bounces = 6
scene.render.resolution_x = 1350
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False

scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -0.35

# Prefer an available GPU backend, falling back to CPU without failing setup.
device_report = []
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for backend in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = backend
            prefs.get_devices()
            enabled = 0
            for device in prefs.devices:
                use = device.type == backend
                device.use = use
                if use:
                    enabled += 1
                    device_report.append(f"{backend}:{device.name}")
            if enabled:
                scene.cycles.device = "GPU"
                break
        except Exception:
            continue
except Exception as exc:
    device_report.append(f"CPU fallback: {exc}")

bpy.context.window.scene = scene
print("scene", scene.name)
print("camera", cam.location[:], cam.data.lens)
print("devices", device_report)
