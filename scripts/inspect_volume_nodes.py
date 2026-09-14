import bpy
import json

m = bpy.data.materials.get("Volume.001")
info = {"found": m is not None, "nodes": [], "links": []}
if m is not None and m.use_nodes:
    for n in m.node_tree.nodes:
        entry = {"name": n.name, "type": n.type}
        if n.type == "PRINCIPLED_VOLUME":
            for sname in ("Density", "Anisotropy"):
                s = n.inputs.get(sname)
                entry[sname] = (round(float(s.default_value), 4)
                                if s is not None and not s.is_linked else "LINKED")
        info["nodes"].append(entry)
    for l in m.node_tree.links:
        info["links"].append(
            f"{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")
print(json.dumps(info, ensure_ascii=False, indent=1))
