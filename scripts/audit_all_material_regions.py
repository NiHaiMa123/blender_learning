import bpy
from collections import Counter
from mathutils import Vector

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")

vertices = obj.data.vertices
for slot_index, slot in enumerate(obj.material_slots):
    material = slot.material
    if not material:
        continue
    polygons = [polygon for polygon in obj.data.polygons if polygon.material_index == slot_index]
    points = [vertices[index].co for polygon in polygons for index in polygon.vertices]
    if not points:
        continue
    mins = [min(point[index] for point in points) for index in range(3)]
    maxs = [max(point[index] for point in points) for index in range(3)]
    nodes = material.node_tree.nodes if material.use_nodes and material.node_tree else []
    image_names = [node.image.name for node in nodes if node.type == "TEX_IMAGE" and node.image]
    shader = next((node for node in nodes if node.name == "mmd_shader"), None)
    group = shader.node_tree.name if shader and shader.node_tree else "-"
    sphere = any(node.name == "mmd_sphere_tex" for node in nodes)
    pbr = [node.name for node in nodes if node.name.startswith("Codex Metal PBR")]
    center = tuple(round((mins[index] + maxs[index]) * 0.5, 3) for index in range(3))
    size = tuple(round(maxs[index] - mins[index], 3) for index in range(3))
    print(
        f"{slot_index:02d} | {material.name:12s} | polys={len(polygons):5d} | center={center} | size={size} | sphere={sphere} | pbr={','.join(pbr) or '-'} | group={group} | tex={','.join(image_names)}"
    )
