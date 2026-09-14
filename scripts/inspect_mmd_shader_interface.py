import bpy
import json

groups = {}
for material in bpy.data.materials:
    if not material.use_nodes or not material.node_tree:
        continue
    for node in material.node_tree.nodes:
        if node.type != "GROUP" or not node.node_tree or node.node_tree.name in groups:
            continue
        group = node.node_tree
        groups[group.name] = {
            "inputs": [
                {"name": socket.name, "type": socket.socket_type}
                for socket in group.interface.items_tree
                if getattr(socket, "in_out", None) == "INPUT"
            ],
            "outputs": [
                {"name": socket.name, "type": socket.socket_type}
                for socket in group.interface.items_tree
                if getattr(socket, "in_out", None) == "OUTPUT"
            ],
            "nodes": [node.type for node in group.nodes],
        }

print(json.dumps(groups, ensure_ascii=False, indent=2))
