import bpy
import json

targets = ["头饰金属", "项链金属", "外裙子", "袖子", "皮肤", "face"]
report = []
for name in targets:
    material = bpy.data.materials.get(name)
    if not material or not material.node_tree:
        continue
    row = {"material": name, "tag": material.get("codex_material_optimization")}
    shader = material.node_tree.nodes.get("mmd_shader")
    if shader:
        row["group"] = shader.node_tree.name if shader.node_tree else None
        row["mmd"] = {socket.name: list(socket.default_value) if hasattr(socket.default_value, "__len__") else socket.default_value for socket in shader.inputs if socket.name in {"Specular Color", "Reflect"}}
        mix = shader.node_tree.nodes.get("混合着色器") if shader.node_tree else None
        row["glossy_mix"] = mix.inputs[0].default_value if mix else None
    bsdf = material.node_tree.nodes.get("Skin Principled") or next((node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        row["skin"] = {socket.name: list(socket.default_value) if hasattr(socket.default_value, "__len__") else socket.default_value for socket in bsdf.inputs if socket.name in {"Subsurface Weight", "Subsurface Radius", "Roughness"}}
    report.append(row)
print(json.dumps(report, ensure_ascii=False, indent=2))
