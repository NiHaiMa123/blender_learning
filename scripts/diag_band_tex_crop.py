import bpy
import json

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
skin_slot = next((i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == "皮肤"), None)
mat = obj.material_slots[skin_slot].material
image = mat.node_tree.nodes["Skin Base Texture"].image
W, H = image.size
px = image.pixels[:]
uv_layer = obj.data.uv_layers.active

us, vs = [], []
for poly in obj.data.polygons:
    if poly.material_index != skin_slot:
        continue
    c = poly.center
    if not (c.x < -0.02 and 0.60 <= c.z <= 0.80):
        continue
    for i in poly.loop_indices:
        uv = uv_layer.data[i].uv
        us.append(uv.x)
        vs.append(uv.y)

print(json.dumps({"faces_u": [round(min(us), 4), round(max(us), 4)],
                  "faces_v": [round(min(vs), 4), round(max(vs), 4)],
                  "size": [W, H]}))

# crop in pixels with margin
pad = 0.01
x0 = max(0, int((min(us) - pad) * W))
x1 = min(W, int((max(us) + pad) * W))
y1_top = max(0, int((1.0 - max(vs) - pad) * H))  # row of max v
y0_bot = min(H, int((1.0 - min(vs) + pad) * H))


def to_srgb(c):
    c = max(0.0, min(1.0, c))
    if c <= 0.0031308:
        return c * 12.92
    return 1.055 * (c ** (1.0 / 2.4)) - 0.055


import os
out_dir = r"D:\project\blender_learning\renders\_preview_right_leg_uv_1080p"
crop_w, crop_h = x1 - x0, y0_bot - y1_top
img = bpy.data.images.new("CodexBandTexCrop", crop_w, crop_h, alpha=False)
pixels = [0.0] * (crop_w * crop_h * 4)
for row in range(crop_h):
    src_y = y1_top + row
    for col in range(crop_w):
        src_x = x0 + col
        o = (src_y * W + src_x) * 4
        d = (row * crop_w + col) * 4
        pixels[d] = to_srgb(float(px[o]))
        pixels[d + 1] = to_srgb(float(px[o + 1]))
        pixels[d + 2] = to_srgb(float(px[o + 2]))
        pixels[d + 3] = 1.0
img.pixels[:] = pixels
img.file_format = "PNG"
img.filepath_raw = os.path.join(out_dir, "band_texture_crop.png")
img.save()
bpy.data.images.remove(img)
print(json.dumps({"crop": [x0, y1_top, x1, y0_bot], "saved": "band_texture_crop.png"}))
