import bpy
import json
from mathutils import Vector
from mathutils.kdtree import KDTree


obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")
mesh = obj.data
uv_layers = mesh.uv_layers
active = uv_layers.active
if active is None:
    raise RuntimeError("Active UV layer not found")

skin_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "皮肤"), None)
if skin_slot is None:
    raise RuntimeError("Original skin material slot not found")

backup_name = "Codex UV Backup Before Right Leg Mirror"
backup = uv_layers.get(backup_name)
if backup is None:
    backup = uv_layers.new(name=backup_name)
    for source, target in zip(active.data, backup.data):
        target.uv = source.uv
active_index = next(index for index, layer in enumerate(uv_layers) if layer == active)
uv_layers.active_index = active_index

z_min = 0.03
z_max = 0.90
x_limit = 0.22
source_polygons = []
target_polygons = []
for poly in mesh.polygons:
    if poly.material_index != skin_slot:
        continue
    center = poly.center
    if not (z_min <= center.z <= z_max and abs(center.x) <= x_limit):
        continue
    if center.x > 0.02:
        source_polygons.append(poly)
    elif center.x < -0.02:
        target_polygons.append(poly)

if not source_polygons or not target_polygons:
    raise RuntimeError("Could not find symmetric skin leg polygons")

tree = KDTree(len(source_polygons))
for index, poly in enumerate(source_polygons):
    center = poly.center
    tree.insert(( -center.x, center.y, center.z), index)
tree.balance()

assignments = []
center_distances = []
vertex_distances = []
for target_poly in target_polygons:
    center = target_poly.center
    _, source_index, center_distance = tree.find((center.x, center.y, center.z))
    source_poly = source_polygons[source_index]
    center_distances.append(center_distance)
    source_loops = list(source_poly.loop_indices)
    for target_loop_index in target_poly.loop_indices:
        target_vertex = mesh.vertices[mesh.loops[target_loop_index].vertex_index].co
        mirrored = Vector((-target_vertex.x, target_vertex.y, target_vertex.z))
        source_loop_index = min(
            source_loops,
            key=lambda index: (mesh.vertices[mesh.loops[index].vertex_index].co - mirrored).length,
        )
        source_vertex = mesh.vertices[mesh.loops[source_loop_index].vertex_index].co
        vertex_distances.append((source_vertex - mirrored).length)
        assignments.append((target_loop_index, active.data[source_loop_index].uv.copy()))

for target_loop_index, uv in assignments:
    active.data[target_loop_index].uv = uv

mesh.update()
obj["codex_right_leg_uv_mirror"] = "source_positive_x_to_negative_x"
obj["codex_right_leg_uv_mirror_faces"] = len(target_polygons)

print(json.dumps({
    "target_faces": len(target_polygons),
    "source_faces": len(source_polygons),
    "uv_assignments": len(assignments),
    "max_center_distance": max(center_distances),
    "max_vertex_distance": max(vertex_distances),
    "backup_uv_layer": backup_name,
}, indent=2))
