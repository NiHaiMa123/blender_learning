import bpy
import json
from collections import defaultdict

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
metal_slot = next((i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == "metal leg"), None)
skin_slot = next((i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == "皮肤"), None)
uv_active = obj.data.uv_layers.active
uv1 = obj.data.uv_layers.get("UV1")

report = {"metal_slot": metal_slot, "uv_layers": [l.name for l in obj.data.uv_layers]}
zbins = defaultdict(int)
xs, ys, zs = [], [], []
for poly in obj.data.polygons:
    if poly.material_index != metal_slot:
        continue
    c = poly.center
    xs.append(c.x)
    ys.append(c.y)
    zs.append(c.z)
    zbins[round(c.z, 2)] += 1
report["metal_faces"] = len(xs)
if xs:
    report["bbox_x"] = [round(min(xs), 4), round(max(xs), 4)]
    report["bbox_y"] = [round(min(ys), 4), round(max(ys), 4)]
    report["bbox_z"] = [round(min(zs), 4), round(max(zs), 4)]
    report["z_hist"] = dict(sorted(zbins.items()))

# UV bbox of metal faces on UV1 and active UV
for label, layer in (("UV1", uv1), ("active", uv_active)):
    if layer is None:
        continue
    us, vs = [], []
    for poly in obj.data.polygons:
        if poly.material_index != metal_slot:
            continue
        for i in poly.loop_indices:
            uv = layer.data[i].uv
            us.append(uv.x)
            vs.append(uv.y)
    report[f"metal_uv_{label}"] = {"u": [round(min(us), 4), round(max(us), 4)],
                                   "v": [round(min(vs), 4), round(max(vs), 4)]}

# metal leg material nodes
mmat = obj.material_slots[metal_slot].material
report["metal_mat_nodes"] = sorted([n.name for n in mmat.node_tree.nodes]) if mmat.use_nodes else []
tex = mmat.node_tree.nodes.get("mmd_base_tex") if mmat.use_nodes else None
if tex is not None and tex.image:
    report["metal_image"] = {"name": tex.image.name, "size": list(tex.image.size)}

print(json.dumps(report, ensure_ascii=False, indent=1))
