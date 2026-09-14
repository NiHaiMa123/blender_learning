import bpy
import json
import os
from bpy_extras.object_utils import world_to_camera_view

scene = bpy.data.scenes["Codex_Cycles_Render"]
cam = scene.camera
obj = bpy.data.objects.get("卡提希娅_mesh")
depsgraph = bpy.context.evaluated_depsgraph_get()
eval_obj = obj.evaluated_get(depsgraph)
mesh = eval_obj.to_mesh()

xs, ys, zs = [], [], []
outside = 0
for vertex in mesh.vertices:
    co_world = eval_obj.matrix_world @ vertex.co
    co_ndc = world_to_camera_view(scene, cam, co_world)
    xs.append(float(co_ndc.x))
    ys.append(float(co_ndc.y))
    zs.append(float(co_ndc.z))
    if co_ndc.x < 0 or co_ndc.x > 1 or co_ndc.y < 0 or co_ndc.y > 1:
        outside += 1
eval_obj.to_mesh_clear()

materials = []
for slot in obj.material_slots:
    mat = slot.material
    if not mat:
        continue
    alpha_links = []
    transparent_nodes = []
    missing_images = []
    if mat.use_nodes and mat.node_tree:
        for node in mat.node_tree.nodes:
            if node.type in {"BSDF_TRANSPARENT", "HOLDOUT"}:
                transparent_nodes.append(node.name)
            if node.type == "BSDF_PRINCIPLED":
                alpha = node.inputs.get("Alpha")
                if alpha:
                    alpha_links.extend(link.from_node.name for link in alpha.links)
            if node.type == "TEX_IMAGE" and node.image:
                image = node.image
                path = bpy.path.abspath(image.filepath) if image.filepath else ""
                if image.source == "FILE" and not image.packed_file and path and not os.path.exists(path):
                    missing_images.append({"image": image.name, "path": path})
    if alpha_links or transparent_nodes or missing_images or mat.diffuse_color[3] < 0.999:
        materials.append({
            "name": mat.name,
            "diffuse_alpha": round(float(mat.diffuse_color[3]), 4),
            "alpha_links": alpha_links,
            "transparent_nodes": transparent_nodes,
            "missing_images": missing_images,
        })

report = {
    "object": obj.name,
    "hide_render": obj.hide_render,
    "vertex_count": len(xs),
    "camera_ndc_bounds": {
        "x": [round(min(xs), 4), round(max(xs), 4)],
        "y": [round(min(ys), 4), round(max(ys), 4)],
        "depth": [round(min(zs), 4), round(max(zs), 4)],
    },
    "vertices_outside_frame": outside,
    "material_slot_count": len(obj.material_slots),
    "transparent_or_missing_materials": materials,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
