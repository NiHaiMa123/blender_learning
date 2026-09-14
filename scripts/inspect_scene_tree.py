import bpy
import json
from collections import Counter

report = {}
# all top-level + recursive scene inventory
def walk(coll, depth=0):
    node = {"name": coll.name, "objects": len(coll.objects),
            "types": dict(Counter(o.type for o in coll.objects))}
    node["children"] = [walk(ch, depth + 1) for ch in coll.children]
    return node

report["scene_tree"] = [walk(c) for c in bpy.context.scene.collection.children]

# duplicates (.001 etc)
names = [c.name for c in bpy.data.collections]
report["collection_dupes"] = sorted([n for n in names if ".00" in n])
obj_names = [o.name for o in bpy.data.objects]
report["object_dupes"] = sorted([n for n in obj_names if ".00" in n])[:40]
report["object_dupe_count"] = sum(1 for n in obj_names if ".00" in n)

# unlinked collections (in data, not reachable from scene)
reachable = set()
def mark(coll):
    reachable.add(coll.name)
    for ch in coll.children:
        mark(ch)
for c in bpy.context.scene.collection.children:
    mark(c)
report["unlinked_collections"] = sorted(
    [c.name for c in bpy.data.collections if c.name not in reachable])[:40]
report["unlinked_collection_count"] = sum(
    1 for c in bpy.data.collections if c.name not in reachable)

# linked-scene object total
seen = set()
for coll in bpy.context.scene.collection.children_recursive:
    seen.update(coll.objects)
report["linked_objects"] = len(seen)
report["orphan_objects"] = len(bpy.data.objects) - len(seen)

# cameras and their collections
report["cameras"] = [
    {"name": o.name, "collections": [c.name for c in o.users_collection]}
    for o in bpy.data.objects if o.type == "CAMERA"]

print(json.dumps(report, ensure_ascii=False, indent=1))
