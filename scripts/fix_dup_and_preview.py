import bpy
import json
import os

report = {}
scene_root = bpy.context.scene.collection

# 1. remove duplicate top-level link (keep the one nested under 场景)
dup = bpy.data.collections.get("体积雾加灯光")
top_names = [c.name for c in scene_root.children]
if dup is not None and dup.name in top_names:
    scene_root.children.unlink(dup)
    report["dup_unlinked"] = True
else:
    report["dup_unlinked"] = False
report["top_collections"] = [c.name for c in scene_root.children]

# 2. save the file with the imported scene
bpy.ops.wm.save_mainfile()
report["saved"] = bpy.data.filepath

# 3. preview render from the scene camera in EEVEE (authorial intent),
#    then restore camera + engine
scene = bpy.context.scene
cam_new = bpy.data.objects.get("摄像机")
old_camera = scene.camera
old_engine = scene.render.engine
old_res = (scene.render.resolution_x, scene.render.resolution_y,
           scene.render.resolution_percentage, scene.render.filepath)
old_dof = (None, None)
try:
    cam_obj = None
    if cam_new is not None and cam_new.type == "CAMERA":
        # find the camera object (may share name with datablock; prefer one in 集合 12)
        cands = [o for o in bpy.data.objects
                 if o.type == "CAMERA" and o.data and o.data.name == "摄像机"]
        cam_obj = next((o for o in cands
                        if "集合 12" in [c.name for c in o.users_collection]), cands[0] if cands else None)
    report["preview_camera"] = cam_obj.name if cam_obj else None
    if cam_obj is None:
        raise RuntimeError("appended camera object not found")
    scene.camera = cam_obj
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 50
    scene.render.image_settings.file_format = "PNG"
    preview_path = r"D:\project\blender_learning\renders\lakeside_import_preview.png"
    scene.render.filepath = preview_path
    bpy.ops.render.render(write_still=True)
    report["preview"] = preview_path
finally:
    scene.camera = old_camera
    scene.render.engine = old_engine
    (scene.render.resolution_x, scene.render.resolution_y,
     scene.render.resolution_percentage, scene.render.filepath) = old_res

print(json.dumps(report, ensure_ascii=False, indent=1))
