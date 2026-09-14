import bpy

group = bpy.data.node_groups.get("MMDShaderDev")
if not group:
    raise RuntimeError("MMDShaderDev not found")

for node in group.nodes:
    if node.type == "MATH":
        values = [socket.default_value for socket in node.inputs]
        print(node.name, node.operation, values)
