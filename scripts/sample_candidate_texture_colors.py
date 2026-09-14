import bpy
import colorsys
import json
from collections import Counter

TARGETS = {"鞋子", "前带子两条", "外裙子", "外裙子2", "外裙子前外", "外裙子内侧", "外裙子内里", "头饰", "项链花"}
obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
uv_layer = obj.data.uv_layers.active
rows = []

for slot_index, slot in enumerate(obj.material_slots):
    material = slot.material
    if not material or material.name not in TARGETS or not uv_layer:
        continue
    texture = material.node_tree.nodes.get("mmd_base_tex") if material.use_nodes and material.node_tree else None
    image = texture.image if texture and texture.type == "TEX_IMAGE" else None
    if not image or image.size[0] == 0 or image.size[1] == 0:
        continue
    pixels = image.pixels
    width, height = image.size
    histogram = Counter()
    colors = []
    polygons = [poly for poly in obj.data.polygons if poly.material_index == slot_index]
    for poly in polygons[::max(1, len(polygons) // 500)]:
        uv = [uv_layer.data[index].uv for index in poly.loop_indices]
        u = sum(value.x for value in uv) / len(uv)
        v = sum(value.y for value in uv) / len(uv)
        x = max(0, min(width - 1, int(u * (width - 1))))
        y = max(0, min(height - 1, int((1.0 - v) * (height - 1))))
        offset = (y * width + x) * 4
        rgb = tuple(float(pixels[offset + channel]) for channel in range(3))
        hue, saturation, value = colorsys.rgb_to_hsv(*rgb)
        if saturation > 0.12 and value > 0.08:
            histogram[int(hue * 24) % 24] += 1
        colors.append({"rgb": [round(value, 3) for value in rgb], "hsv": [round(hue, 3), round(saturation, 3), round(value, 3)]})
    rows.append({
        "material": material.name,
        "image": image.name,
        "image_size": list(image.size),
        "samples": len(colors),
        "hue_bins": histogram.most_common(8),
        "sample_colors": colors[:12],
    })

print(json.dumps(rows, ensure_ascii=False, indent=2))
