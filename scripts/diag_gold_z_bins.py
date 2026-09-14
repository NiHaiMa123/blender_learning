import bpy
import json
import colorsys
from collections import defaultdict

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
skin_slot = next((i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == "皮肤"), None)
mat = obj.material_slots[skin_slot].material
image = mat.node_tree.nodes["Skin Base Texture"].image
W, H = image.size
px = image.pixels[:]
uv_layer = obj.data.uv_layers.active

def texel(uv):
    x = max(0, min(W - 1, int(uv[0] * (W - 1))))
    y = max(0, min(H - 1, int((1.0 - uv[1]) * (H - 1))))
    o = (y * W + x) * 4
    return (float(px[o]), float(px[o+1]), float(px[o+2]))

def gold_class(rgb):
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    dh = abs(h - 0.08)
    dh = min(dh, 1.0 - dh)
    return (dh < 0.035) and (s > 0.40) and (0.12 < v < 0.82)

zbins = defaultdict(lambda: {"gold": 0, "skin": 0, "gold_rgb": [0, 0, 0], "skin_rgb": [0, 0, 0]})
for poly in obj.data.polygons:
    if poly.material_index != skin_slot:
        continue
    c = poly.center
    if not (c.x < -0.02 and 0.60 <= c.z <= 0.80):
        continue
    uvs = [uv_layer.data[i].uv for i in poly.loop_indices]
    ux = sum(u.x for u in uvs) / len(uvs)
    uy = sum(u.y for u in uvs) / len(uvs)
    rgb = texel((ux, uy))
    key = round(c.z + 1e-9, 2)
    if gold_class(rgb):
        zbins[key]["gold"] += 1
        for i in range(3):
            zbins[key]["gold_rgb"][i] += rgb[i]
    else:
        zbins[key]["skin"] += 1
        for i in range(3):
            zbins[key]["skin_rgb"][i] += rgb[i]

rows = []
for z in sorted(zbins):
    d = zbins[z]
    row = {"z": z, "gold_faces": d["gold"], "skin_faces": d["skin"]}
    if d["gold"]:
        row["gold_avg"] = [round(v / d["gold"], 3) for v in d["gold_rgb"]]
    if d["skin"]:
        row["skin_avg"] = [round(v / d["skin"], 3) for v in d["skin_rgb"]]
    rows.append(row)
print(json.dumps(rows, indent=1))
