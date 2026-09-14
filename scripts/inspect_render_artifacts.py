import bpy
import json

scene = bpy.context.scene
lights = []
for obj in scene.objects:
    if obj.type == "LIGHT":
        data = obj.data
        lights.append({
            "name": obj.name,
            "type": data.type,
            "location": list(obj.location),
            "energy": data.energy,
            "visible_camera": getattr(data, "visible_camera", None),
            "visible_glossy": getattr(data, "visible_glossy", None),
        })

meshes = []
for obj in scene.objects:
    if obj.type != "MESH" or obj.name == "鸣潮_今汐_桃夭灼灼1.0311_mesh":
        continue
    materials = [slot.material.name for slot in obj.material_slots if slot.material]
    if obj.parent is None or any(token in obj.name.lower() for token in ("light", "sphere", "lamp", "area", "point", "sun")):
        meshes.append({
            "name": obj.name,
            "location": list(obj.location),
            "dimensions": list(obj.dimensions),
            "materials": materials,
        })

print(json.dumps({"lights": lights, "meshes": meshes}, ensure_ascii=False, indent=2))
