import bpy
import json

mat = bpy.data.materials.get("皮肤")
tree = mat.node_tree
nodes = []
for n in tree.nodes:
    inp = {}
    for s in n.inputs:
        if s.is_linked:
            inp[s.name] = "LINKED"
        else:
            try:
                v = s.default_value
                if hasattr(v, "__len__") and not isinstance(v, (str, bytes)):
                    inp[s.name] = [round(float(x), 4) for x in v] if len(v) <= 4 else f"len{len(v)}"
                elif isinstance(v, float):
                    inp[s.name] = round(v, 4)
                else:
                    inp[s.name] = v
            except Exception:
                inp[s.name] = "?"
    nodes.append({"name": n.name, "type": n.type, "label": n.label, "inputs": inp})

links = []
for l in tree.links:
    links.append(f"{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")

print(json.dumps({"nodes": nodes, "links": links}, ensure_ascii=False, indent=2))
