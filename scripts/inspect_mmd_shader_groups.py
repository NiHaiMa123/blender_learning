import bpy
import json

obj = bpy.data.objects.get("卡提希娅_mesh")
targets = {"Face_", "Up_Skin", "Hair_Bangs", "Hair_Bangs+", "Hair_Back", "Hair_Back+"}
report = []

for slot in obj.material_slots:
    mat = slot.material
    if not mat or mat.name not in targets or not mat.use_nodes:
        continue
    item = {"material": mat.name, "top_nodes": [], "groups": []}
    for node in mat.node_tree.nodes:
        n = {"name": node.name, "type": node.type}
        if node.type == 'GROUP' and node.node_tree:
            n["tree"] = node.node_tree.name
            n["inputs"] = [
                {"name": s.name, "type": s.type, "default": str(getattr(s, "default_value", "")), "linked": s.is_linked}
                for s in node.inputs
            ]
            group = {"name": node.node_tree.name, "nodes": [], "links": []}
            for gn in node.node_tree.nodes:
                gd = {"name": gn.name, "type": gn.type}
                if gn.type == 'GROUP' and gn.node_tree:
                    gd["tree"] = gn.node_tree.name
                if gn.type in {'MIX_SHADER', 'BSDF_TRANSPARENT', 'BSDF_PRINCIPLED', 'SHADER_TO_RGB'}:
                    gd["inputs"] = [
                        {"name": s.name, "default": str(getattr(s, "default_value", "")), "linked": s.is_linked}
                        for s in gn.inputs
                    ]
                group["nodes"].append(gd)
            group["links"] = [f"{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}" for l in node.node_tree.links]
            item["groups"].append(group)
        if node.type == 'TEX_IMAGE' and node.image:
            n["image"] = node.image.name
            n["alpha_mode"] = node.image.alpha_mode
        item["top_nodes"].append(n)
    report.append(item)

print(json.dumps(report, ensure_ascii=False, indent=2))
return_value = json.dumps(report, ensure_ascii=False, indent=2)
