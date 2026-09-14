import bpy
import json

mat = bpy.data.materials.get("皮肤")
tree = mat.node_tree
out = {"blender_version": list(bpy.app.version)}
for name in ("Codex Band Lift Z In", "Codex Band Lift Z Out", "Codex Band Lift X Feather",
             "Codex Band Lift Gain R", "Codex Band Lift Not Gold", "Codex Band Lift Mix"):
    n = tree.nodes.get(name)
    if n is None:
        out[name] = None
        continue
    info = {"bl_idname": n.bl_idname, "type": n.type}
    if n.type == "MAP_RANGE":
        info["data_type"] = n.data_type
        info["interpolation"] = n.interpolation_type
        info["clamp"] = bool(n.clamp)
    socks = []
    for i, s in enumerate(n.inputs):
        try:
            v = s.default_value
            if hasattr(v, "__len__") and not isinstance(v, (str, bytes)):
                val = [round(float(x), 4) for x in v]
            elif isinstance(v, float):
                val = round(v, 4)
            else:
                val = str(v)
        except Exception as e:
            val = f"<err>"
        socks.append({"index": i, "name": s.name, "linked": s.is_linked, "value": val})
    info["inputs"] = socks
    out[name] = info
print(json.dumps(out, ensure_ascii=False, indent=1))
