import bpy
import json
from collections import Counter

obj = bpy.data.objects["卡提希娅_mesh"]
poly_counts = Counter(poly.material_index for poly in obj.data.polygons)
rows = []
for index, slot in enumerate(obj.material_slots):
    mat = slot.material
    if not mat:
        continue
    row = {
        "index": index,
        "name": mat.name,
        "polygons": poly_counts.get(index, 0),
        "diffuse_alpha": round(float(mat.diffuse_color[3]), 4),
        "use_nodes": mat.use_nodes,
        "use_backface_culling": getattr(mat, "use_backface_culling", None),
        "surface_render_method": getattr(mat, "surface_render_method", None),
        "nodes": [],
        "links": [],
    }
    if mat.use_nodes and mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type in {"OUTPUT_MATERIAL", "BSDF_PRINCIPLED", "BSDF_TRANSPARENT", "MIX_SHADER", "MIX", "TEX_IMAGE"}:
                entry = {"name": node.name, "type": node.type}
                if node.type == "TEX_IMAGE" and node.image:
                    entry.update({
                        "image": node.image.name,
                        "filepath": bpy.path.abspath(node.image.filepath),
                        "alpha_mode": node.image.alpha_mode,
                    })
                if node.type == "BSDF_PRINCIPLED":
                    alpha = node.inputs.get("Alpha")
                    entry["alpha_default"] = float(alpha.default_value) if alpha else None
                row["nodes"].append(entry)
        for link in mat.node_tree.links:
            if link.to_node.type in {"OUTPUT_MATERIAL", "BSDF_PRINCIPLED", "MIX_SHADER", "MIX"}:
                row["links"].append(
                    f"{link.from_node.name}.{link.from_socket.name} -> {link.to_node.name}.{link.to_socket.name}"
                )
    rows.append(row)

print(json.dumps(rows, ensure_ascii=False, indent=2))
