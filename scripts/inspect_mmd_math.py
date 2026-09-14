import bpy, json

tree = bpy.data.node_groups.get("MMDShaderDev")
rows = []
for node in tree.nodes:
    if node.type == 'MATH':
        rows.append({
            "name": node.name,
            "operation": node.operation,
            "inputs": [{"name": s.name, "default": getattr(s, "default_value", None), "linked": s.is_linked} for s in node.inputs],
            "outgoing": [f"{l.to_node.name}.{l.to_socket.name}" for l in node.outputs[0].links],
        })
return_value = json.dumps(rows, ensure_ascii=False, indent=2)
print(return_value)
