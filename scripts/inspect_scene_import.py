import bpy
import json
import os

report = {
    "filepath": bpy.data.filepath,
    "is_dirty": bool(bpy.data.is_dirty),
    "version": list(bpy.app.version),
    "scenes": [s.name for s in bpy.data.scenes],
    "active_scene": bpy.context.scene.name,
    "render_engine": bpy.context.scene.render.engine,
}

# character-related objects
char_objs = [o for o in bpy.data.objects
             if "今汐" in o.name or "鸣潮" in o.name]
report["character_objects"] = [
    {"name": o.name, "type": o.type,
     "hide_viewport": bool(o.hide_viewport),
     "hide_render": bool(o.hide_render),
     "collections": [c.name for c in o.users_collection]}
    for o in char_objs][:30]
report["character_object_count"] = len(char_objs)

# top-level collections
report["collections"] = [c.name for c in bpy.context.scene.collection.children]

# peek into the lakeside .blend without linking
lib = r"D:\software\blender\blender_models\场景\夜晚湖畔场景配布\夜晚湖畔场景配布版.blend"
report["lib_exists"] = os.path.exists(lib)
report["lib_size_mb"] = round(os.path.getsize(lib) / 1048576, 1) if os.path.exists(lib) else 0
try:
    with bpy.data.libraries.load(lib, link=False) as (src, _):
        report["lib_scenes"] = list(src.scenes)
        report["lib_collections"] = list(src.collections)
        report["lib_worlds"] = list(src.worlds)
        report["lib_cameras"] = list(src.cameras)
        report["lib_object_count"] = len(src.objects)
        report["lib_objects_sample"] = list(src.objects)[:20]
        report["lib_images"] = list(src.images)[:20]
        report["lib_image_count"] = len(src.images)
except Exception as e:
    report["lib_error"] = str(e)

print(json.dumps(report, ensure_ascii=False, indent=1))
