import bpy
import json


TARGETS = {
    "皮肤", "脸", "face", "Cheek", "袖子", "袖子2", "外裙子", "外裙子2",
    "外裙子内侧", "外裙子内里", "外裙子前外", "纱内侧", "纱外侧", "鞋子",
    "头饰金属", "耳坠", "项链金属", "项链花", "metal leg",
}


def scalar(value):
    if hasattr(value, "__len__"):
        return [round(float(item), 3) for item in value]
    return round(float(value), 3)


for name in sorted(TARGETS):
    mat = bpy.data.materials.get(name)
    if not mat or not mat.use_nodes or not mat.node_tree:
        continue
    tree = mat.node_tree
    nodes = []
    for node in tree.nodes:
        item = {"name": node.name, "type": node.type}
        if node.type == "BSDF_PRINCIPLED":
            for socket_name in ("Metallic", "Roughness", "IOR", "Subsurface Weight", "Subsurface"):
                socket = node.inputs.get(socket_name)
                if socket is not None:
                    item[socket_name] = scalar(socket.default_value)
        if node.type == "GROUP":
            item["group"] = node.node_tree.name if node.node_tree else None
        nodes.append(item)
    links = [
        f"{link.from_node.name}:{link.from_socket.name}->{link.to_node.name}:{link.to_socket.name}"
        for link in tree.links
    ]
    print(json.dumps({"material": name, "nodes": nodes, "links": links}, ensure_ascii=False, separators=(",", ":")))
