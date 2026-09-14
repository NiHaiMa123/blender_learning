import bpy, json
empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
arm = next((o for o in bpy.data.objects if o.type=="ARMATURE" and o.parent is not None and o.parent.name==empty.name), None)
names = [b.name for b in arm.pose.bones if "指" in b.name]
print(json.dumps({"fingers": sorted(names)}, ensure_ascii=False, indent=1))
