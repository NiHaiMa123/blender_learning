import bpy
import json
import os

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")
uv_layer = obj.data.uv_layers.active


def sample_region(material_name, z_min, z_max):
    slot_indices = {
        index for index, slot in enumerate(obj.material_slots)
        if slot.material and slot.material.name == material_name
    }
    material = bpy.data.materials.get(material_name)
    node = material.node_tree.nodes.get("Skin Base Texture") if material and material.node_tree else None
    image = node.image if node else None
    if image is None:
        return {}
    width, height = image.size
    regions = {"left_x": [], "right_x": []}
    for poly in obj.data.polygons:
        if poly.material_index not in slot_indices:
            continue
        center = poly.center
        if not (z_min <= center.z <= z_max):
            continue
        side = "left_x" if center.x < -0.02 else "right_x" if center.x > 0.02 else None
        if side is None:
            continue
        uvs = [uv_layer.data[index].uv for index in poly.loop_indices]
        uv = sum(uvs, uvs[0].copy()) / (len(uvs) + 1)
        x = max(0, min(width - 1, int(uv.x * (width - 1))))
        y = max(0, min(height - 1, int((1.0 - uv.y) * (height - 1))))
        offset = (y * width + x) * 4
        regions[side].append([float(image.pixels[offset + channel]) for channel in range(3)])
    result = {}
    for side, colors in regions.items():
        result[side] = {
            "samples": len(colors),
            "average_rgb": [sum(color[channel] for color in colors) / len(colors) for channel in range(3)] if colors else None,
            "min_rgb": [min(color[channel] for color in colors) for channel in range(3)] if colors else None,
            "max_rgb": [max(color[channel] for color in colors) for channel in range(3)] if colors else None,
        }
    return result


skin = bpy.data.materials.get("皮肤")
metal = bpy.data.materials.get("metal leg")
metal_node = metal.node_tree.nodes.get("Codex Metal PBR metal leg") if metal and metal.node_tree else None
tint_node = metal.node_tree.nodes.get("Codex Metal Tint metal leg") if metal and metal.node_tree else None
metal_texture = metal.node_tree.nodes.get("mmd_base_tex") if metal and metal.node_tree else None

report = {
    "skin_texture": {
        "image": skin.node_tree.nodes.get("Skin Base Texture").image.name if skin and skin.node_tree.nodes.get("Skin Base Texture") else None,
        "ring_band": sample_region("皮肤", 0.62, 0.78),
        "above_ring": sample_region("皮肤", 0.78, 0.90),
        "below_ring": sample_region("皮肤", 0.45, 0.62),
    },
    "metal_leg": {
        "tag": metal.get("codex_material_optimization") if metal else None,
        "texture": metal_texture.image.name if metal_texture and metal_texture.image else None,
        "texture_size": list(metal_texture.image.size) if metal_texture and metal_texture.image else None,
        "pbr_metallic": float(metal_node.inputs["Metallic"].default_value) if metal_node else None,
        "pbr_roughness": float(metal_node.inputs["Roughness"].default_value) if metal_node else None,
        "tint_factor": float(tint_node.inputs[0].default_value) if tint_node else None,
        "tint_color": list(tint_node.inputs[2].default_value) if tint_node else None,
    },
}
print(json.dumps(report, ensure_ascii=False, indent=2))
