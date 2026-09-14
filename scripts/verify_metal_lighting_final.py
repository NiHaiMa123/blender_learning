import bpy
import json
import os

batch_dir = r"D:\project\blender_learning\renders\今汐_4K_front_back_face_20260905_222127"
image_names = ("01_front_full_4k.png", "02_back_full_4k.png", "03_face_front_4k.png")
images = []
for name in image_names:
    image = bpy.data.images.load(os.path.join(batch_dir, name), check_existing=False)
    images.append(image)

materials = {}
for name in ("头饰金属", "耳坠", "项链金属", "metal leg"):
    material = bpy.data.materials.get(name)
    node = material.node_tree.nodes.get(f"Codex Metal PBR {name}") if material and material.node_tree else None
    materials[name] = {
        "tag": material.get("codex_material_optimization") if material else None,
        "pbr_node": node.name if node else None,
        "metallic": float(node.inputs["Metallic"].default_value) if node else None,
        "roughness": float(node.inputs["Roughness"].default_value) if node else None,
    }

lights = {}
for name in ("Key_Soft", "Fill_Front", "Rim_Cool", "Overhead_Soft", "Side_Fill_Left", "Back_Fill_Warm", "Metal_Strip_Key", "Metal_Strip_Rim"):
    light = bpy.data.objects.get(name)
    if light and light.type == "LIGHT":
        lights[name] = {"energy": light.data.energy, "location": list(light.location)}

print(json.dumps({
    "images": {name: list(image.size) for name, image in zip(image_names, images)},
    "materials": materials,
    "lights": lights,
    "lanterns_hidden": all(
        bpy.data.objects[name].hide_render
        for name in ("Lantern_A", "Lantern_B", "Lantern_C")
        if bpy.data.objects.get(name)
    ),
}, ensure_ascii=False, indent=2))

for image in images:
    bpy.data.images.remove(image)
