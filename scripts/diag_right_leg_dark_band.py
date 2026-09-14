import bpy
import json
from collections import defaultdict

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
report = {"object_found": obj is not None}
if obj is not None:
    report["active_uv"] = obj.data.uv_layers.active.name if obj.data.uv_layers.active else None
    # skin slot + texture
    skin_slot = next((i for i, s in enumerate(obj.material_slots) if s.material and s.material.name == "皮肤"), None)
    report["skin_slot"] = skin_slot
    tex_node = None
    image = None
    if skin_slot is not None:
        mat = obj.material_slots[skin_slot].material
        report["skin_blend_method"] = mat.blend_method if hasattr(mat, "blend_method") else None
        if mat.use_nodes and mat.node_tree:
            tex_node = mat.node_tree.nodes.get("Skin Base Texture")
            report["tex_node_found"] = tex_node is not None
            if tex_node is not None:
                image = tex_node.image
                report["image"] = {"name": image.name if image else None,
                                   "size": list(image.size) if image else None,
                                   "filepath": image.filepath if image and image.filepath else ""}
            # skin principled inputs
            skin_shader = mat.node_tree.nodes.get("Skin Principled")
            if skin_shader is not None:
                vals = {}
                for key in ("Base Color", "Subsurface Weight", "Subsurface Color", "Subsurface Radius",
                            "Metallic", "Roughness", "IOR", "Alpha"):
                    sock = skin_shader.inputs.get(key)
                    if sock is not None:
                        try:
                            v = sock.default_value
                            vals[key] = list(v) if hasattr(v, "__len__") and not isinstance(v, (float, int)) else v
                        except Exception as e:
                            vals[key] = f"<err {e}>"
                report["skin_principled"] = vals
            # overlay nodes present?
            report["overlay_nodes"] = sorted([n.name for n in mat.node_tree.nodes if n.name.startswith("Codex Baked Ring")])
            # check mix factor links
            mix = mat.node_tree.nodes.get("Codex Baked Ring Mix")
            if mix is not None:
                report["ring_mix_fac_linked"] = mix.inputs[0].is_linked

    # Sample texture colors by spatial region (uses active UV)
    if skin_slot is not None and image is not None:
        uv_layer = obj.data.uv_layers.active
        W, H = image.size
        px = image.pixels[:]

        def sample_poly(poly):
            uvs = [uv_layer.data[i].uv for i in poly.loop_indices]
            ux = sum(u.x for u in uvs) / len(uvs)
            uy = sum(u.y for u in uvs) / len(uvs)
            x = max(0, min(W - 1, int(ux * (W - 1))))
            y = max(0, min(H - 1, int((1.0 - uy) * (H - 1))))
            o = (y * W + x) * 4
            return [float(px[o]), float(px[o+1]), float(px[o+2])]

        buckets = defaultdict(list)
        for poly in obj.data.polygons:
            if poly.material_index != skin_slot:
                continue
            c = poly.center
            if c.x < -0.02:  # character right leg
                if 0.62 <= c.z <= 0.78:
                    buckets["R_ring_band"].append(poly)
                elif 0.50 <= c.z < 0.62:
                    buckets["R_below_band"].append(poly)
                elif 0.78 < c.z <= 0.92:
                    buckets["R_above_band"].append(poly)
            elif c.x > 0.02:  # character left leg
                if 0.62 <= c.z <= 0.78:
                    buckets["L_same_height"].append(poly)
                elif 0.50 <= c.z < 0.62:
                    buckets["L_below"].append(poly)

        region_stats = {}
        for name, polys in buckets.items():
            cols = [sample_poly(p) for p in polys[:400]]
            if cols:
                n = len(cols)
                avg = [sum(c[k] for c in cols)/n for k in range(3)]
                region_stats[name] = {"faces": len(polys), "sampled": n,
                                      "avg_rgb": [round(v, 4) for v in avg]}
            else:
                region_stats[name] = {"faces": 0, "sampled": 0, "avg_rgb": None}
        report["texture_region_stats"] = region_stats

    # Overlapping / co-located faces from other slots in ring band volume
    co = defaultdict(int)
    for poly in obj.data.polygons:
        c = poly.center
        if c.x < -0.02 and 0.55 <= c.z <= 0.85:
            mat = obj.material_slots[poly.material_index].material
            co[mat.name if mat else "<none>"] += 1
    report["slots_in_R_thigh_volume"] = dict(co)

# Other mesh objects that could occlude legs (same bounding area)
occluders = []
for o in bpy.data.objects:
    if o.type != "MESH" or o is obj or o.hide_render:
        continue
    try:
        ws = [o.matrix_world @ v.co for v in o.data.vertices]
    except Exception:
        continue
    if not ws:
        continue
    xs = [v.x for v in ws]; ys = [v.y for v in ws]; zs = [v.z for v in ws]
    # overlaps thigh corridor?
    if min(xs) < 0.1 and max(xs) > -0.2 and min(zs) < 0.85 and max(zs) > 0.5:
        occluders.append({"name": o.name, "verts": len(ws),
                          "x": [round(min(xs),3), round(max(xs),3)],
                          "y": [round(min(ys),3), round(max(ys),3)],
                          "z": [round(min(zs),3), round(max(zs),3)],
                          "hide_viewport": o.hide_viewport, "hide_render": o.hide_render})
report["possible_occluders"] = occluders[:20]

# Lights
lights = []
for o in bpy.data.objects:
    if o.type == "LIGHT":
        d = o.data
        lights.append({"name": o.name, "type": d.type, "energy": round(float(d.energy),1),
                       "color": [round(v,3) for v in d.color],
                       "use_shadow": bool(d.use_shadow),
                       "loc": [round(v,3) for v in o.location]})
report["lights"] = sorted(lights, key=lambda r: r["name"])

# Render / world / view
scene = bpy.context.scene
report["render"] = {"engine": scene.render.engine,
                    "exposure": getattr(scene.view_settings, "exposure", None),
                    "film_transparent": scene.render.film_transparent}
if scene.world and scene.world.use_nodes:
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        report["world_bg"] = {"color": [round(v,4) for v in bg.inputs["Color"].default_value],
                              "strength": round(float(bg.inputs["Strength"].default_value),4)}

print(json.dumps(report, ensure_ascii=False, indent=2))
