import bpy
import json
import os

batch_dir = r"D:\project\blender_learning\renders\今汐_4K_front_back_face_20260906_004650"
names = ("01_front_full_4k.png", "02_back_full_4k.png", "03_face_front_4k.png")
images = [bpy.data.images.load(os.path.join(batch_dir, name), check_existing=False) for name in names]
obj = bpy.data.objects["鸣潮_今汐_桃夭灼灼1.0311_mesh"]
skin = bpy.data.materials["皮肤"]
metal = bpy.data.materials["metal leg"]
ring_slot = next(index for index, slot in enumerate(obj.material_slots) if slot.material == metal)
shoe_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "Codex Shoe Heel Metal"), None)

print(json.dumps({
    "images": {name: list(image.size) for name, image in zip(names, images)},
    "skin_ring_overlay": skin.get("codex_baked_ring_metal_overlay"),
    "metal_leg_pbr": bool(metal.node_tree.nodes.get("Codex Metal PBR metal leg")),
    "uv_layers": [layer.name for layer in obj.data.uv_layers],
    "mirror_backup_present": bool(obj.data.uv_layers.get("Codex UV Backup Before Right Leg Mirror")),
    "skin_lift_slot_present": bool(bpy.data.materials.get("Codex Skin Right Leg Lift")),
    "ring_faces": sum(1 for poly in obj.data.polygons if poly.material_index == ring_slot),
    "shoe_heel_faces": sum(1 for poly in obj.data.polygons if poly.material_index == shoe_slot) if shoe_slot is not None else 0,
}, ensure_ascii=False, indent=2))

for image in images:
    bpy.data.images.remove(image)
