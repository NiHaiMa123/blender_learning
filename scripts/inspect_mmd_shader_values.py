import bpy
import json

TARGETS = {"头饰金属", "耳坠", "项链金属", "项链花", "外裙子", "外裙子2", "外裙子内侧", "外裙子内里", "外裙子前外", "袖子", "袖子2", "鞋子", "皮肤"}


def val(value):
    if hasattr(value, "__len__"):
        return [round(float(item), 4) for item in value]
    return round(float(value), 4)


for name in sorted(TARGETS):
    mat = bpy.data.materials.get(name)
    if not mat or not mat.node_tree:
        continue
    shader = next((node for node in mat.node_tree.nodes if node.name == "mmd_shader"), None)
    if not shader:
        continue
    inputs = {socket.name: val(socket.default_value) for socket in shader.inputs if not socket.is_linked}
    group = shader.node_tree
    internals = []
    for node in group.nodes:
        if node.type in {"BSDF_GLOSSY", "BSDF_DIFFUSE", "MIX_SHADER", "BSDF_TRANSPARENT"}:
            item = {"name": node.name, "type": node.type}
            for socket_name in ("Color", "Roughness", "Weight", "Fac"):
                socket = node.inputs.get(socket_name)
                if socket is not None and not socket.is_linked:
                    item[socket_name] = val(socket.default_value)
            internals.append(item)
    print(json.dumps({"material": name, "inputs": inputs, "internals": internals}, ensure_ascii=False, separators=(",", ":")))
