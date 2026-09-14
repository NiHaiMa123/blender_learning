import bpy
import json

coll = bpy.data.collections.get("路灯")
report = {"found": coll is not None, "items": []}
if coll is not None:
    for o in coll.all_objects:
        entry = {"name": o.name, "type": o.type,
                 "loc": [round(v, 3) for v in o.location]}
        if o.type == "MESH" and o.data and o.data.materials:
            mats = []
            for m in o.data.materials:
                if m is None or not m.use_nodes:
                    mats.append({"name": m.name if m else None, "emission": "?"})
                    continue
                emis = [n for n in m.node_tree.nodes
                        if n.type in ("EMISSION", "BSDF_PRINCIPLED")]
                info = {"name": m.name, "has_emission_node": any(n.type == "EMISSION" for n in emis)}
                for n in m.node_tree.nodes:
                    if n.type == "EMISSION":
                        try:
                            info["emission_strength"] = round(float(n.inputs["Strength"].default_value), 2)
                            info["emission_color"] = [round(float(v), 3) for v in n.inputs["Color"].default_value]
                        except Exception:
                            pass
                mats.append(info)
            entry["materials"] = mats
        if o.type == "LIGHT":
            entry["energy"] = round(float(o.data.energy), 1)
            entry["color"] = [round(float(v), 3) for v in o.data.color]
        report["items"].append(entry)

print(json.dumps(report, ensure_ascii=False, indent=1))
