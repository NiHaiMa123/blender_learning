import bpy

seen = set()
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    for slot in obj.material_slots:
        if slot.material and slot.material.name not in seen:
            seen.add(slot.material.name)

print("\n".join(sorted(seen)))
