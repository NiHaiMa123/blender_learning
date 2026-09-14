import bpy
import json
import os
from datetime import datetime

scene = bpy.context.scene
cam = next((o for o in bpy.data.objects
            if o.type == "CAMERA" and o.data and o.data.name == "摄像机"), None)
if cam is None:
    raise RuntimeError("appended camera not found")

batch_name = f"夜晚湖畔_Cycles4K_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
batch_dir = os.path.join(r"D:\project\blender_learning\renders", batch_name)
os.makedirs(batch_dir, exist_ok=True)

# record state
old_camera = scene.camera
old_engine = scene.render.engine
old_world = scene.world
old_res = (scene.render.resolution_x, scene.render.resolution_y,
           scene.render.resolution_percentage,
           scene.render.image_settings.file_format,
           scene.render.image_settings.color_mode,
           scene.render.filepath)
old_cycles = (scene.cycles.samples, scene.cycles.use_adaptive_sampling,
              scene.cycles.adaptive_threshold, scene.cycles.use_denoising)

# lights inside 场景 subtree + author char rig stay; all other lights hidden
scene_coll = bpy.data.collections.get("场景")
rig_coll = bpy.data.collections.get("人物灯光（b站搜三分仪打光教程）")
keep = set()
for coll in [c for c in (scene_coll, rig_coll) if c is not None]:
    for sub in [coll] + list(coll.children_recursive):
        keep.update(sub.objects)
hidden_lights = []
for o in bpy.data.objects:
    if o.type == "LIGHT" and o not in keep:
        hidden_lights.append((o, o.hide_render))
        o.hide_render = True

# author's night world if present
world002 = bpy.data.worlds.get("World.002")
world_info = None
if world002 is not None and world002.use_nodes:
    bg = world002.node_tree.nodes.get("Background")
    if bg is not None:
        world_info = {
            "color": [round(float(v), 4) for v in bg.inputs["Color"].default_value],
            "strength": round(float(bg.inputs["Strength"].default_value), 4),
        }

rendered = None
try:
    if world002 is not None:
        scene.world = world002
    scene.camera = cam
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.cycles.samples = max(scene.cycles.samples, 128)
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = min(scene.cycles.adaptive_threshold, 0.015)
    scene.cycles.use_denoising = True
    out = os.path.join(batch_dir, "01_lakeside_night_4k.png")
    scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    rendered = out
finally:
    for o, hide in hidden_lights:
        o.hide_render = hide
    scene.camera = old_camera
    scene.render.engine = old_engine
    scene.world = old_world
    (scene.render.resolution_x, scene.render.resolution_y,
     scene.render.resolution_percentage,
     scene.render.image_settings.file_format,
     scene.render.image_settings.color_mode,
     scene.render.filepath) = old_res
    (scene.cycles.samples, scene.cycles.use_adaptive_sampling,
     scene.cycles.adaptive_threshold, scene.cycles.use_denoising) = old_cycles

manifest = {
    "batch": batch_name,
    "engine": "CYCLES",
    "resolution": [3840, 2160],
    "camera": cam.name,
    "world": scene.world.name if scene.world else None,
    "world_rendered": world002.name if world002 else None,
    "world_bg": world_info,
    "samples": 128,
    "hidden_lights": sorted([o.name for o, _ in hidden_lights]),
    "shots": [rendered],
}
with open(os.path.join(batch_dir, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(json.dumps(manifest, ensure_ascii=False, indent=1))
