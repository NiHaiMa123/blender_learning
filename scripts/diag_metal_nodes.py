import bpy
import json

mat = bpy.data.materials.get("metal leg")
tree = mat.node_tree
out = {"nodes": [], "links": []}
for n in tree.nodes:
    out["nodes"].append({"name": n.name, "type": n.type})
for l in tree.links:
    out["links"].append(
        f"{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")
print(json.dumps(out, ensure_ascii=False, indent=1))
