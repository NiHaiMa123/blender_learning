import bpy
import colorsys
import json

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
uv_layer = obj.data.uv_layers.active
slot_index = next(index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "metal leg")
material = obj.material_slots[slot_index].material
texture = material.node_tree.nodes.get("mmd_base_tex")
image = texture.image
width, height = image.size
colors = []
for poly in obj.data.polygons:
    if poly.material_index != slot_index:
        continue
    uvs = [uv_layer.data[index].uv for index in poly.loop_indices]
    uv = sum(uvs, uvs[0].copy()) / (len(uvs) + 1)
    x = max(0, min(width - 1, int(uv.x * (width - 1))))
    y = max(0, min(height - 1, int((1.0 - uv.y) * (height - 1))))
    offset = (y * width + x) * 4
    rgb = tuple(float(image.pixels[offset + channel]) for channel in range(3))
    colors.append(rgb)

print(json.dumps({
    "image": image.name,
    "samples": len(colors),
    "average_rgb": [sum(color[channel] for color in colors) / len(colors) for channel in range(3)],
    "min_rgb": [min(color[channel] for color in colors) for channel in range(3)],
    "max_rgb": [max(color[channel] for color in colors) for channel in range(3)],
    "average_hsv": [
        sum(colorsys.rgb_to_hsv(*color)[channel] for color in colors) / len(colors)
        for channel in range(3)
    ],
}, indent=2))
