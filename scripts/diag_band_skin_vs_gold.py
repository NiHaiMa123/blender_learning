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
    return (float(px[o]), float(px[o+1]), float(px[o+2]), float(px[o+3]))

def is_gold(rgb):
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    dh = abs(h - 0.08)
    dh = min(dh, 1.0 - dh)
    return (dh < 0.035) and (s > 0.40) and (0.12 < v < 0.82)

buckets = defaultdict(list)
buckets_alpha = defaultdict(list)
for poly in obj.data.polygons:
    if poly.material_index != skin_slot:
        continue
    c = poly.center
    uvs = [uv_layer.data[i].uv for i in poly.loop_indices]
    ux = sum(u.x for u in uvs) / len(uvs)
    uy = sum(u.y for u in uvs) / len(uvs)
    r, g, b, a = texel((ux, uy))
    key = None
    if c.x < -0.02 and 0.62 <= c.z <= 0.78:
        key = "R_band_gold" if is_gold((r, g, b)) else "R_band_skin"
    elif c.x > 0.02 and 0.62 <= c.z <= 0.78:
        key = "L_skin"
    elif c.x < -0.02 and 0.78 < c.z <= 0.92:
        key = "R_above"
    if key is None:
        continue
    buckets[key].append((r, g, b))
    buckets_alpha[key].append(a)

out = {}
for k, cols in buckets.items():
    n = len(cols)
    avg = [sum(c[i] for c in cols)/n for i in range(3)] if n else None
    aa = buckets_alpha[k]
    out[k] = {"samples": n,
              "avg_rgb": [round(v, 4) for v in avg] if avg else None,
              "avg_alpha": round(sum(aa)/len(aa), 4) if aa else None,
              "min_alpha": round(min(aa), 4) if aa else None}
    if avg and k in ("R_band_skin", "L_skin") and out.get("L_skin", {}).get("avg_rgb"):
        pass

# gain needed: L_skin / R_band_skin per channel
if out.get("R_band_skin", {}).get("avg_rgb") and out.get("L_skin", {}).get("avg_rgb"):
    rb = out["R_band_skin"]["avg_rgb"]
    lb = out["L_skin"]["avg_rgb"]
    out["gain_L_over_Rbandskin"] = [round(lb[i]/rb[i] if rb[i] > 1e-6 else 0, 4) for i in range(3)]
if out.get("R_above", {}).get("avg_rgb") and out.get("R_band_skin", {}).get("avg_rgb"):
    ra = out["R_above"]["avg_rgb"]
    rb = out["R_band_skin"]["avg_rgb"]
    out["gain_Rabove_over_Rbandskin"] = [round(ra[i]/rb[i] if rb[i] > 1e-6 else 0, 4) for i in range(3)]

print(json.dumps(out, indent=2))
