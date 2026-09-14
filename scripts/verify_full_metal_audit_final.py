import bpy
import json
import os
from collections import Counter

batch_dir = r"D:\project\blender_learning\renders\今汐_4K_front_back_face_20260905_234251"
image_names = ("01_front_full_4k.png", "02_back_full_4k.png", "03_face_front_4k.png")
images = []
for name in image_names:
    images.append(bpy.data.images.load(os.path.join(batch_dir, name), check_existing=False))

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
material_audit = {}
for name in ("头饰金属", "耳坠", "项链金属", "metal leg", "鞋子"):
    material = bpy.data.materials.get(name)
    nodes = material.node_tree.nodes if material and material.use_nodes and material.node_tree else []
    material_audit[name] = {
        "tag": material.get("codex_material_optimization") if material else None,
        "explicit_pbr": any(node.name.startswith("Codex Metal PBR") for node in nodes),
        "gold_mask": bool(material.get("codex_gold_texture_mask")) if material else False,
        "warm_tint": bool(material.get("codex_metal_tint")) if material else False,
    }

gold_mask_materials = []
for material in bpy.data.materials:
    if material.get("codex_gold_texture_mask"):
        gold_mask_materials.append(material.name)

heel_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "Codex Shoe Heel Metal"), None)
heel_faces = sum(1 for poly in obj.data.polygons if poly.material_index == heel_slot) if heel_slot is not None else 0
lift_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "Codex Skin Right Leg Lift"), None)
lift_faces = sum(1 for poly in obj.data.polygons if poly.material_index == lift_slot) if lift_slot is not None else 0

print(json.dumps({
    "images": {name: list(image.size) for name, image in zip(image_names, images)},
    "materials": material_audit,
    "gold_mask_materials": sorted(gold_mask_materials),
    "shoe_heel_slot": heel_slot,
    "shoe_heel_faces": heel_faces,
    "ring_skin_lift_slot": lift_slot,
    "ring_skin_lift_faces": lift_faces,
    "leg_fill_energy": {
        name: bpy.data.objects[name].data.energy
        for name in ("Leg_Fill_Front", "Leg_Fill_Right", "Leg_Fill_Left", "Leg_Fill_Ring")
        if bpy.data.objects.get(name)
    },
    "lanterns_hidden": all(
        bpy.data.objects[name].hide_render
        for name in ("Lantern_A", "Lantern_B", "Lantern_C")
        if bpy.data.objects.get(name)
    ),
}, ensure_ascii=False, indent=2))

for image in images:
    bpy.data.images.remove(image)
