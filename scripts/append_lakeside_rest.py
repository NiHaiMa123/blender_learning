import bpy
import json
import os

LIB = r"D:\software\blender\blender_models\场景\夜晚湖畔场景配布\夜晚湖畔场景配布版.blend"
SKIP = {"场景", "RigidBodyWorld", "RigidBodyConstraints"}
report = {}

# 1. link 场景 if not linked
scene_coll = bpy.data.collections.get("场景")
if scene_coll is not None:
    linked = [c.name for c in bpy.context.scene.collection.children]
    if scene_coll.name not in linked:
        bpy.context.scene.collection.children.link(scene_coll)
        report["scene_linked_now"] = True
    else:
        report["scene_linked_now"] = False

# 2. append all remaining collections
with bpy.data.libraries.load(LIB, link=False) as (src, dst):
    available = [str(c) for c in src.collections]
    existing = set(c.name for c in bpy.data.collections)
    names = [c for c in available if c not in SKIP and c not in existing]
    dst.collections = names
    report["requested"] = list(names)

# 3. link newly appended collections that have no parent (true top-level)
all_colls = list(bpy.data.collections)
child_names = set()
for c in all_colls:
    for ch in c.children:
        child_names.add(ch.name)
scene_child_names = set(c.name for c in bpy.context.scene.collection.children)
linked_now = []
for name in report["requested"]:
    if name in child_names:
        continue
    if name in scene_child_names:
        continue
    bpy.context.scene.collection.children.link(bpy.data.collections[name])
    linked_now.append(name)
report["top_level_linked"] = linked_now

# 4. totals + missing images
total_objs = len(bpy.data.objects)
linked_objs = set()
for coll in bpy.context.scene.collection.children_recursive:
    linked_objs.update(coll.objects)
report["total_objects_data"] = total_objs

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
        missing.append(img.name)
report["packed_images"] = packed
report["missing_image_count"] = len(missing)
report["missing_images"] = missing[:30]
report["top_collections"] = [c.name for c in bpy.context.scene.collection.children]

print(json.dumps(report, ensure_ascii=False, indent=1))
