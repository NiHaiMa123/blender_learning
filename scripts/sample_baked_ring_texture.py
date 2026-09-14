import bpy
import colorsys
import json
from collections import Counter

obj = bpy.data.objects["鸣潮_今汐_桃夭灼灼1.0311_mesh"]
uv_layer = obj.data.uv_layers.active
skin_slot = next(index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "皮肤")
material = obj.material_slots[skin_slot].material
image = material.node_tree.nodes["Skin Base Texture"].image
width, height = image.size
samples = []
for poly in obj.data.polygons:
    if poly.material_index != skin_slot:
        continue
    center = poly.center
    if not (center.x < -0.02 and 0.62 <= center.z <= 0.78):
        continue
    uvs = [uv_layer.data[index].uv for index in poly.loop_indices]
    uv = sum(uvs, uvs[0].copy()) / (len(uvs) + 1)
    x = max(0, min(width - 1, int(uv.x * (width - 1))))
    y = max(0, min(height - 1, int((1.0 - uv.y) * (height - 1))))
    offset = (y * width + x) * 4
    rgb = tuple(float(image.pixels[offset + channel]) for channel in range(3))
    samples.append({"rgb": rgb, "hsv": colorsys.rgb_to_hsv(*rgb)})

hue_bins = Counter(int(sample["hsv"][0] * 36) % 36 for sample in samples if sample["hsv"][1] > 0.1)
sat_bins = Counter(int(sample["hsv"][1] * 10) for sample in samples)
print(json.dumps({
    "samples": len(samples),
    "hue_bins": hue_bins.most_common(12),
    "saturation_bins": sat_bins.most_common(12),
    "dark_saturated": sum(1 for sample in samples if sample["hsv"][1] > 0.25 and sample["hsv"][2] < 0.75),
}, indent=2))
