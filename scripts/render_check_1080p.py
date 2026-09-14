import bpy, os
scene = bpy.context.scene
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
out_dir = r"D:\project\blender_learning\renders\_preview_right_leg_uv_1080p"
os.makedirs(out_dir, exist_ok=True)
old_camera = scene.camera
old_engine = scene.render.engine
old_world = scene.world
old_res = (scene.render.resolution_x, scene.render.resolution_y,
           scene.render.resolution_percentage, scene.render.filepath)
old_cycles = (scene.cycles.samples, scene.cycles.use_adaptive_sampling,
              scene.cycles.adaptive_threshold, scene.cycles.use_denoising)
scene_coll = bpy.data.collections.get("场景")
rig_coll = bpy.data.collections.get("人物灯光（b站搜三分仪打光教程）")
keep = set()
for coll in [c for c in (scene_coll, rig_coll) if c is not None]:
    for sub in [coll] + list(coll.children_recursive):
        keep.update(sub.objects)
hidden = []
for o in bpy.data.objects:
    if o.type == "LIGHT" and o not in keep:
        hidden.append((o, o.hide_render))
        o.hide_render = True
world002 = bpy.data.worlds.get("World.002")
try:
    if world002 is not None:
        scene.world = world002
    scene.camera = cam
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.render.filepath = os.path.join(out_dir, "refcheck_1080p.png")
    bpy.ops.render.render(write_still=True)
finally:
    for o, h in hidden:
        o.hide_render = h
    scene.camera = old_camera
    scene.render.engine = old_engine
    scene.world = old_world
    (scene.render.resolution_x, scene.render.resolution_y,
     scene.render.resolution_percentage, scene.render.filepath) = old_res
    (scene.cycles.samples, scene.cycles.use_adaptive_sampling,
     scene.cycles.adaptive_threshold, scene.cycles.use_denoising) = old_cycles
print("refcheck 1080p done")
