import bpy
import json

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
mesh = obj.data
active = mesh.uv_layers.active
backup = mesh.uv_layers.get("Codex UV Backup Before Right Leg Mirror")
ring_slot = next(index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "metal leg")

ring_loop_indices = [
    loop_index
    for poly in mesh.polygons
    if poly.material_index == ring_slot
    for loop_index in poly.loop_indices
]
diffs = []
if active and backup:
    diffs = [
        (active.data[index].uv - backup.data[index].uv).length
        for index in ring_loop_indices
    ]

metal = bpy.data.materials.get("metal leg")
tex_uv = metal.node_tree.nodes.get("mmd_tex_uv") if metal and metal.node_tree else None
uv_links = []
if tex_uv and tex_uv.node_tree:
    uv_links = [
        f"{link.from_node.name}:{link.from_socket.name}->{link.to_node.name}:{link.to_socket.name}"
        for link in tex_uv.node_tree.links
    ]

print(json.dumps({
    "uv_layers": [layer.name for layer in mesh.uv_layers],
    "active_uv": active.name if active else None,
    "backup_uv": backup.name if backup else None,
    "ring_faces": sum(1 for poly in mesh.polygons if poly.material_index == ring_slot),
    "ring_uv_max_diff_from_backup": max(diffs) if diffs else None,
    "ring_uv_average_diff_from_backup": sum(diffs) / len(diffs) if diffs else None,
    "metal_uv_group_links": uv_links,
}, ensure_ascii=False, indent=2))
