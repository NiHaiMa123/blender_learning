import bpy

group = bpy.data.node_groups.get("MMDShaderDev")
if not group:
    raise RuntimeError("MMDShaderDev not found")

for link in group.links:
    print(f"{link.from_node.name}:{link.from_socket.name} -> {link.to_node.name}:{link.to_socket.name}")
