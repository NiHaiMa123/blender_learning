import bpy
import json
import os

BACKUP = r"D:\software\blender\project\今汐_before_lakeside_import_backup.blend"
report = {
    "backup_exists": os.path.exists(BACKUP),
    "backup_size_mb": round(os.path.getsize(BACKUP) / 1048576, 1) if os.path.exists(BACKUP) else 0,
}

char_coll = bpy.data.collections.get("人物")
report["character_hidden_viewport"] = bool(char_coll.hide_viewport) if char_coll else None
report["character_hidden_render"] = bool(char_coll.hide_render) if char_coll else None

scene_coll = bpy.data.collections.get("场景")
report["scene_collection_present"] = scene_coll is not None
report["scene_linked_to_scene"] = (
    scene_coll.name in [c.name for c in bpy.context.scene.collection.children]
    if scene_coll else False)
if scene_coll is not None:
    all_objs = scene_coll.all_objects
    report["scene_objects"] = len(all_objs)
    by_type = {}
    for o in all_objs:
        by_type[o.type] = by_type.get(o.type, 0) + 1
    report["scene_by_type"] = by_type
    report["scene_children"] = [c.name for c in scene_coll.children]
    report["objects_without_data"] = sum(
        1 for o in all_objs if o.type == "MESH" and o.data is None)

# duplicate check: how many collections named 场景* exist
report["scene_name_variants"] = sorted(
    [c.name for c in bpy.data.collections if c.name.startswith("场景")])

# missing external images across whole file
missing = []
packed = 0
for img in bpy.data.images:
    if img.source != "FILE":
        continue
    if img.packed_file is not None:
        packed += 1
        continue
    path = bpy.path.abspath(img.filepath) if img.filepath else ""
    if not path or not os.path.exists(path):
        missing.append({"name": img.name, "filepath": img.filepath})
report["packed_images"] = packed
report["missing_images"] = missing[:30]
report["missing_image_count"] = len(missing)
report["worlds"] = [w.name for w in bpy.data.worlds]

print(json.dumps(report, ensure_ascii=False, indent=1))
