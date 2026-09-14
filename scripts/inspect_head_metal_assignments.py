import bpy
import json
from collections import defaultdict
from mathutils import Vector

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")

vertices = obj.data.vertices
rows = []
for slot_index, slot in enumerate(obj.material_slots):
    material = slot.material
    if not material or not any(token in material.name for token in ("头", "耳", "项链", "带子", "花")):
        continue
    polygons = [polygon for polygon in obj.data.polygons if polygon.material_index == slot_index]
    points = [vertices[index].co for polygon in polygons for index in polygon.vertices]
    if not points:
        continue
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    material_nodes = material.node_tree.nodes if material.use_nodes and material.node_tree else []
    shader = next((node for node in material_nodes if node.name == "mmd_shader"), None)
    group = shader.node_tree.name if shader and shader.node_tree else None
    specular = None
    reflect = None
    mix = None
    if shader:
        specular_socket = shader.inputs.get("Specular Color")
        reflect_socket = shader.inputs.get("Reflect")
        specular = list(specular_socket.default_value) if specular_socket else None
        reflect = float(reflect_socket.default_value) if reflect_socket else None
        if shader.node_tree:
            mix_node = shader.node_tree.nodes.get("混合着色器")
            if mix_node:
                mix = float(mix_node.inputs[0].default_value)
    rows.append({
        "slot": slot_index,
        "material": material.name,
        "polygons": len(polygons),
        "local_bounds": {"min": mins, "max": maxs},
        "shader_group": group,
        "specular_color": specular,
        "reflect": reflect,
        "glossy_mix": mix,
        "images": [node.image.name for node in material_nodes if node.type == "TEX_IMAGE" and node.image],
    })

print(json.dumps(rows, ensure_ascii=False, indent=2))
