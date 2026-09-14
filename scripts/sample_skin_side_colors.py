import bpy
import json

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
slot_index = next(index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "皮肤")
material = obj.material_slots[slot_index].material
texture = material.node_tree.nodes.get("Skin Base Texture")
image = texture.image
uv_layer = obj.data.uv_layers.active

regions = {
    "left_ring_leg": [],
    "right_leg": [],
}
for poly in obj.data.polygons:
    if poly.material_index != slot_index:
        continue
    center = poly.center
    if not (0.48 < center.z < 0.90):
        continue
    key = "left_ring_leg" if center.x < -0.02 else "right_leg" if center.x > 0.02 else None
    if key is None:
        continue
    uvs = [uv_layer.data[index].uv for index in poly.loop_indices]
    uv = sum(uvs, uvs[0].copy()) / (len(uvs) + 1)
    width, height = image.size
    x = max(0, min(width - 1, int(uv.x * (width - 1))))
    y = max(0, min(height - 1, int((1.0 - uv.y) * (height - 1))))
    offset = (y * width + x) * 4
    regions[key].append([float(image.pixels[offset + channel]) for channel in range(3)])

report = {}
for name, colors in regions.items():
    report[name] = {
        "samples": len(colors),
        "average_rgb": [sum(color[channel] for color in colors) / len(colors) for channel in range(3)] if colors else None,
        "min_rgb": [min(color[channel] for color in colors) for channel in range(3)] if colors else None,
        "max_rgb": [max(color[channel] for color in colors) for channel in range(3)] if colors else None,
    }
print(json.dumps(report, indent=2))
