import bpy
import json

report = {}

# volume / fog density
for o in bpy.data.objects:
    if o.type != "MESH" or not o.data or not o.data.materials:
        continue
    for m in o.data.materials:
        if m is None or not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "PRINCIPLED_VOLUME":
                d = n.inputs.get("Density")
                a = n.inputs.get("Anisotropy")
                report.setdefault("volumes", []).append({
                    "object": o.name, "material": m.name,
                    "density": round(float(d.default_value), 4) if d else None,
                    "anisotropy": round(float(a.default_value), 4) if a else None,
                })

# lamp head materials
for mname in ("cgaxis_models_113_05_02", "cgaxis_models_113_05_01", "材质"):
    m = bpy.data.materials.get(mname)
    if m is None or not m.use_nodes:
        report[mname] = None
        continue
    info = {"nodes": sorted([n.name for n in m.node_tree.nodes])}
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            bc = n.inputs.get("Base Color")
            mt = n.inputs.get("Metallic")
            rg = n.inputs.get("Roughness")
            try:
                info["base_color"] = [round(float(v), 3) for v in bc.default_value] if bc else None
                info["metallic"] = round(float(mt.default_value), 3) if mt else None
                info["roughness"] = round(float(rg.default_value), 3) if rg else None
            except Exception:
                pass
    report[mname] = info

# point light energies in 路灯
coll = bpy.data.collections.get("路灯")
lights = []
if coll is not None:
    for o in coll.all_objects:
        if o.type == "LIGHT":
            lights.append({"name": o.name, "energy": round(float(o.data.energy), 1),
                           "radius": round(float(getattr(o.data, "shadow_soft_size", -1)), 4)})
report["street_point_lights"] = lights

# exposure / view
report["exposure"] = getattr(bpy.context.scene.view_settings, "exposure", None)
report["view_transform"] = getattr(bpy.context.scene.view_settings, "view_transform", None)

print(json.dumps(report, ensure_ascii=False, indent=1))
