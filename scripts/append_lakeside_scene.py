import bpy
import json
import os

LIB = r"D:\software\blender\blender_models\场景\夜晚湖畔场景配布\夜晚湖畔场景配布版.blend"
BACKUP = r"D:\software\blender\project\今汐_before_lakeside_import_backup.blend"
report = {}

# 1. backup current file (copy, session stays on original path)
bpy.ops.wm.save_as_mainfile(filepath=BACKUP, copy=True, check_existing=False)
report["backup"] = BACKUP

# 2. hide character collection
char_coll = bpy.data.collections.get("人物")
if char_coll is None:
    raise RuntimeError("collection 人物 not found")
char_coll.hide_viewport = True
char_coll.hide_render = True
report["character_hidden"] = True

# 3. append the master scene collection + world
before_objs = set(bpy.data.objects)
before_colls = set(bpy.data.collections)
with bpy.data.libraries.load(LIB, link=False) as (src, dst):
    dst.collections = ["场景"] if "场景" in src.collections else []
    dst.worlds = ["World.002"] if "World.002" in src.worlds else []
scene_coll = next((c for c in bpy.data.collections if c not in before_colls), None)
report["appended_collection"] = scene_coll.name if scene_coll else None
if scene_coll is not None:
    bpy.context.scene.collection.children.link(scene_coll)
    all_objs = scene_coll.all_objects
    report["scene_objects"] = len(all_objs)
    by_type = {}
    for o in all_objs:
        by_type[o.type] = by_type.get(o.type, 0) + 1
    report["scene_by_type"] = by_type
    report["scene_children"] = [c.name for c in scene_coll.children]
    missing_colls = [o for o in all_objs if o.type == "MESH" and o.data is None]
    report["objects_without_data"] = len(missing_colls)
report["new_objects_total"] = len(set(bpy.data.objects) - before_objs)
report["appended_worlds"] = [w.name for w in bpy.data.worlds]

print(json.dumps(report, ensure_ascii=False, indent=1))
