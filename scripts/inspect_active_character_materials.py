import bpy
import json
from collections import Counter


def socket_value(node, *names):
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            return list(socket.default_value) if hasattr(socket.default_value, "__len__") else float(socket.default_value)
    return None


mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
rows = []
for obj in mesh_objects:
    counts = Counter(poly.material_index for poly in obj.data.polygons)
    for index, slot in enumerate(obj.material_slots):
        mat = slot.material
        if not mat:
            continue
        bsdfs = []
        images = []
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    bsdfs.append({
                        "name": node.name,
                        "base_color": socket_value(node, "Base Color"),
                        "metallic": socket_value(node, "Metallic"),
                        "roughness": socket_value(node, "Roughness"),
                        "subsurface": socket_value(node, "Subsurface Weight", "Subsurface"),
                        "subsurface_radius": socket_value(node, "Subsurface Radius"),
                        "ior": socket_value(node, "IOR"),
                    })
                elif node.type == "TEX_IMAGE":
                    images.append({
                        "name": node.name,
                        "image": node.image.name if node.image else None,
                        "filepath": bpy.path.abspath(node.image.filepath) if node.image else None,
                    })
        rows.append({
            "object": obj.name,
            "slot": index,
            "polygons": counts.get(index, 0),
            "material": mat.name,
            "diffuse_color": list(mat.diffuse_color),
            "surface_render_method": getattr(mat, "surface_render_method", None),
            "bsdfs": bsdfs,
            "images": images,
            "node_names": [node.name for node in mat.node_tree.nodes] if mat.use_nodes and mat.node_tree else [],
        })

print(json.dumps({"objects": [obj.name for obj in mesh_objects], "materials": rows}, ensure_ascii=False, indent=2))
