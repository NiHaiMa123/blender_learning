import bpy, json
out = {"armatures": []}
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        arm = o.data
        bones = []
        for b in arm.bones:
            bones.append({"name": b.name, "parent": b.parent.name if b.parent else None,
                          "head": [round(v,3) for v in b.head_local],
                          "tail": [round(v,3) for v in b.tail_local]})
        cons = {}
        for pb in o.pose.bones:
            if pb.constraints:
                cons[pb.name] = [{"type": c.type, "name": c.name} for c in pb.constraints]
        out["armatures"].append({"obj": o.name, "loc": [round(v,3) for v in o.location],
                                 "rot": [round(v,3) for v in o.rotation_euler],
                                 "parent": o.parent.name if o.parent else None,
                                 "nbones": len(bones), "bones": bones, "constraints": cons})
print(json.dumps(out, ensure_ascii=False, indent=1))
