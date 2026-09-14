import bpy
import json

material = bpy.data.materials.get("metal leg")
shader = material.node_tree.nodes.get("mmd_shader") if material and material.node_tree else None
uv_group = bpy.data.node_groups.get("MMDTexUV")
nodes = []
if uv_group:
    for node in uv_group.nodes:
        if node.type in {"UVMAP", "TEX_COORD", "MAPPING", "VECT_TRANSFORM"}:
            nodes.append({
                "name": node.name,
                "type": node.type,
                "uv_map": getattr(node, "uv_map", None),
                "vector_type": getattr(node, "vector_type", None),
            })

print(json.dumps({
    "material_group": shader.node_tree.name if shader and shader.node_tree else None,
    "uv_group": uv_group.name if uv_group else None,
    "uv_nodes": nodes,
    "mesh_uv_layers": [layer.name for layer in bpy.data.objects["鸣潮_今汐_桃夭灼灼1.0311_mesh"].data.uv_layers],
    "active_uv": bpy.data.objects["鸣潮_今汐_桃夭灼灼1.0311_mesh"].data.uv_layers.active.name,
}, ensure_ascii=False, indent=2))
