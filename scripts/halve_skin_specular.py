import bpy, json
skin = bpy.data.materials.get("皮肤")
p = skin.node_tree.nodes.get("Skin Principled")
rep = {"old_spec": round(float(p.inputs["Specular IOR Level"].default_value),3),
       "old_coat": round(float(p.inputs["Coat Weight"].default_value),3)}
p.inputs["Specular IOR Level"].default_value = rep["old_spec"] * 0.5
p.inputs["Coat Weight"].default_value = rep["old_coat"] * 0.5
rep["new_spec"] = round(float(p.inputs["Specular IOR Level"].default_value),3)
rep["new_coat"] = round(float(p.inputs["Coat Weight"].default_value),3)
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
