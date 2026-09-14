import bpy

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")

source_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "皮肤"), None)
lift_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "Codex Skin Right Leg Lift"), None)
if source_slot is None:
    raise RuntimeError("Original skin slot not found")

restored = 0
if lift_slot is not None:
    for poly in obj.data.polygons:
        if poly.material_index == lift_slot:
            poly.material_index = source_slot
            restored += 1
    obj.data.materials.pop(index=lift_slot)

material = bpy.data.materials.get("Codex Skin Right Leg Lift")
if material and material.users == 0:
    bpy.data.materials.remove(material)

bpy.context.view_layer.update()
print(f"Restored original skin faces: {restored}")
