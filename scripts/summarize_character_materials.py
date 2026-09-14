import bpy
import json
from collections import Counter


def value(node, name):
    socket = node.inputs.get(name)
    if socket is None:
        return None
    raw = socket.default_value
    if hasattr(raw, "__len__"):
        return [round(float(item), 4) for item in raw]
    return round(float(raw), 4)


rows = []
for obj in bpy.context.scene.objects:
    if obj.type != "MESH" or not obj.material_slots:
        continue
    counts = Counter(poly.material_index for poly in obj.data.polygons)
    for index, slot in enumerate(obj.material_slots):
        mat = slot.material
        if not mat:
            continue
        nodes = mat.node_tree.nodes if mat.use_nodes and mat.node_tree else []
        bsdfs = []
        images = []
        for node in nodes:
            if node.type == "BSDF_PRINCIPLED":
                bsdfs.append({
                    "name": node.name,
                    "metallic": value(node, "Metallic"),
                    "roughness": value(node, "Roughness"),
                    "subsurface": value(node, "Subsurface Weight") or value(node, "Subsurface"),
                    "ior": value(node, "IOR"),
                })
            elif node.type == "TEX_IMAGE" and node.image:
                images.append(node.image.name)
        rows.append({
            "object": obj.name,
            "slot": index,
            "polygons": counts.get(index, 0),
            "material": mat.name,
            "bsdfs": bsdfs,
            "images": images,
            "nodes": [node.type for node in nodes],
        })

print(json.dumps(rows, ensure_ascii=False, indent=2))
