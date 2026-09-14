import bpy
import json
import math
from collections import defaultdict, deque
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
settings = mod.settings
collision = mod.collision_settings
body = bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER']
mesh = obj.data


def connected_components(data):
    adjacency = defaultdict(set)
    for edge in data.edges:
        a, b = edge.vertices
        adjacency[a].add(b)
        adjacency[b].add(a)
    seen = set()
    result = []
    for start in range(len(data.vertices)):
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        component = []
        while queue:
            vertex = queue.popleft()
            component.append(vertex)
            for neighbor in adjacency[vertex]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        result.append(component)
    return result


components = connected_components(mesh)
pin_ids = set()
for component in components:
    top = max(mesh.vertices[index].co.z for index in component)
    pin_ids.update(
        index for index in component
        if mesh.vertices[index].co.z >= top - 0.05
    )

# Cloth pinning uses weight 1.0 for fully pinned and 0.0/unassigned for free.
group = obj.vertex_groups.get('CLOTH_PIN_WAIST')
if group is None:
    group = obj.vertex_groups.new(name='CLOTH_PIN_WAIST')
all_ids = [vertex.index for vertex in mesh.vertices]
group.remove(all_ids)
group.add(sorted(pin_ids), 1.0, 'REPLACE')
settings.vertex_group_mass = group.name

body_collision = body.collision
body_collision.use = True
body_collision.use_culling = False
body_collision.use_normal = False
body_collision.thickness_outer = 0.004
body_collision.thickness_inner = 0.002
body_collision.damping = 0.35
body_collision.cloth_friction = 1.0

settings.quality = 7
settings.mass = 0.25
settings.air_damping = 15.0
settings.tension_stiffness = 120.0
settings.compression_stiffness = 120.0
settings.shear_stiffness = 70.0
settings.bending_stiffness = 4.0
settings.tension_damping = 30.0
settings.compression_damping = 30.0
settings.shear_damping = 30.0
settings.bending_damping = 12.0
settings.pin_stiffness = 1.0
settings.time_scale = 0.5
collision.use_collision = True
collision.use_self_collision = False
collision.collision_quality = 5
collision.distance_min = 0.002
collision.damping = 0.5
collision.friction = 0.2

cache = mod.point_cache
cache.use_disk_cache = False
cache.frame_start = 1
cache.frame_end = 80
cache.frame_step = 1
scene.frame_start = 1
scene.frame_end = 80
scene.frame_set(1)

window = bpy.context.window
area = next((item for item in window.screen.areas if item.type == 'VIEW_3D'), None)
region = next((item for item in area.regions if item.type == 'WINDOW'), None) if area else None
override = {'window': window, 'screen': window.screen}
if area and region:
    override.update({'area': area, 'region': region})
with bpy.context.temp_override(**override):
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all()

base = [vertex.co.copy() for vertex in mesh.vertices]
depsgraph = bpy.context.evaluated_depsgraph_get()
samples = []
for frame in [1, 10, 20, 40, 80]:
    scene.frame_set(frame)
    depsgraph.update()
    evaluated = obj.evaluated_get(depsgraph)
    coords = [vertex.co.copy() for vertex in evaluated.data.vertices]
    displacements = [(coords[index] - base[index]).length for index in range(len(coords))]
    pinned_displacements = [displacements[index] for index in pin_ids]
    free_displacements = [displacements[index] for index in range(len(coords)) if index not in pin_ids]
    non_finite = sum(
        1 for coordinate in coords for value in coordinate if not math.isfinite(value)
    )
    center = sum(coords, Vector()) / len(coords)
    samples.append({
        'frame': frame,
        'center': [round(float(value), 6) for value in center],
        'min': [round(min(vertex[axis] for vertex in coords), 6) for axis in range(3)],
        'max': [round(max(vertex[axis] for vertex in coords), 6) for axis in range(3)],
        'pinned_max_displacement': round(max(pinned_displacements), 8),
        'free_mean_displacement': round(sum(free_displacements) / len(free_displacements), 8),
        'free_max_displacement': round(max(free_displacements), 8),
        'non_finite': non_finite,
    })

report = {
    'vertices': len(mesh.vertices),
    'faces': len(mesh.polygons),
    'components': len(components),
    'pin_vertices': len(pin_ids),
    'free_vertices': len(mesh.vertices) - len(pin_ids),
    'pin_weight': 1.0,
    'baked': bool(cache.is_baked),
    'samples': samples,
}
print('CORRECT_PIN_TEST|' + json.dumps(report, ensure_ascii=False))
