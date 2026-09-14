import bpy
import json

mat = bpy.data.materials.get("皮肤")
tree = mat.node_tree
out = {"nodes": sorted([n.name for n in tree.nodes if n.name.startswith("Codex Band Lift")]),
       "links": []}
for l in tree.links:
    a, b = l.from_node.name, l.to_node.name
    if a.startswith("Codex Band Lift") or b in ("Skin Color Balance", "Skin Output"):
        out["links"].append(f"{a}.{l.from_socket.name} -> {b}.{l.to_socket.name}")
print(json.dumps(out, ensure_ascii=False, indent=1))
