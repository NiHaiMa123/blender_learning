import bpy
import json
import os
from collections import defaultdict, deque
from mathutils import Matrix
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
s = mod.settings
c = mod.collision_settings
body = bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER']
body_col = body.collision
mesh = obj.data
armature = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_arm')
character_root = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311')
final_blend = r'D:\software\blender\project\今汐_cloth_rebuild_final.blend'
manifest_dir = r'D:\project\blender_learning\cache\cloth_rebuild_v8'
expected_disk_cache_dir = os.path.join(
    os.path.dirname(final_blend),
    'blendcache_' + os.path.splitext(os.path.basename(final_blend))[0],
)

# Pin the top band of every disconnected skirt panel instead of using one global Z cutoff.
adj = defaultdict(set)
for edge in mesh.edges:
    a, b = edge.vertices
    adj[a].add(b)
    adj[b].add(a)
seen = set()
components = []
for start in range(len(mesh.vertices)):
    if start in seen:
        continue
    q = deque([start])
    seen.add(start)
    comp = []
    while q:
        v = q.popleft()
        comp.append(v)
        for n in adj[v]:
            if n not in seen:
                seen.add(n)
                q.append(n)
    components.append(comp)
pin_ids = []
for comp in components:
    top = max(mesh.vertices[i].co.z for i in comp)
    pin_ids.extend(i for i in comp if mesh.vertices[i].co.z >= top - 0.05)
pin_ids = sorted(set(pin_ids))
vg = obj.vertex_groups['CLOTH_PIN_WAIST']
all_ids = [v.index for v in mesh.vertices]
vg.remove(all_ids)
# Blender Cloth pinning uses weight 1.0 for fully pinned vertices.
# Vertices outside the group remain free; assigning 1.0 to them would invert the solve.
vg.add(pin_ids, 1.0, 'REPLACE')
s.vertex_group_mass = vg.name

# Stable cloth contract: body collision on, self-collision off because the source
# contains layered garment sheets that initially overlap by design.
body.hide_viewport = False
body_col.use = True
body_col.use_culling = False
body_col.use_normal = False
for modifier in list(body.modifiers):
    if modifier.type == 'SOLIDIFY':
        body.modifiers.remove(modifier)
body_col.thickness_outer = 0.004
body_col.thickness_inner = 0.002
body_col.damping = 0.35
body_col.cloth_friction = 1.0
s.quality = 7
s.mass = 0.25
s.air_damping = 15.0
s.tension_stiffness = 120.0
s.compression_stiffness = 120.0
s.shear_stiffness = 70.0
s.bending_stiffness = 4.0
s.tension_damping = 30.0
s.compression_damping = 30.0
s.shear_damping = 30.0
s.bending_damping = 12.0
s.time_scale = 0.5
c.use_collision = True
c.use_self_collision = False
c.collision_quality = 5
c.distance_min = 0.002
c.damping = 0.5
c.friction = 0.2
mod.point_cache.frame_start = 1
mod.point_cache.frame_end = 120
mod.point_cache.frame_step = 1
mod.point_cache.use_disk_cache = True
scene.frame_start = 1
scene.frame_end = 120
os.makedirs(manifest_dir, exist_ok=True)
# Blender names disk cache folders from the currently opened .blend file.
# Save the final filename before baking so reopening this file resolves its cache.
bpy.ops.wm.save_as_mainfile(filepath=final_blend, check_existing=False)
try:
    mod.point_cache.filepath = os.path.join(expected_disk_cache_dir, '')
except Exception:
    pass

scene.frame_set(1)
win = bpy.context.window
area = next((a for a in win.screen.areas if a.type == 'VIEW_3D'), None)
region = next((r for r in area.regions if r.type == 'WINDOW'), None) if area else None
override = {'window': win, 'screen': win.screen}
if area and region:
    override.update({'area': area, 'region': region})
with bpy.context.temp_override(**override):
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all()

depsgraph = bpy.context.evaluated_depsgraph_get()
def sample(frame):
    scene.frame_set(frame)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    coords = [v.co for v in ev.data.vertices]
    center = sum(coords, Vector()) / len(coords)
    mins = [min(v[i] for v in coords) for i in range(3)]
    maxs = [max(v[i] for v in coords) for i in range(3)]
    return {
        'frame': frame,
        'center': [round(float(x), 6) for x in center],
        'min': [round(float(x), 6) for x in mins],
        'max': [round(float(x), 6) for x in maxs],
    }

samples = [sample(f) for f in [1, 20, 40, 80, 120]]
cache_files = []
if os.path.isdir(expected_disk_cache_dir):
    for root, _dirs, files in os.walk(expected_disk_cache_dir):
        for filename in files:
            path = os.path.join(root, filename)
            cache_files.append({
                'path': path,
                'bytes': os.path.getsize(path),
            })
manifest_path = os.path.join(manifest_dir, 'cloth_rebuild_manifest.json')
manifest = {
    'blend': final_blend,
    'simulation': 'Blender Cloth',
    'source_frame': 100,
    'cache_dir': expected_disk_cache_dir,
    'manifest_dir': manifest_dir,
    'frames': [1, 120],
    'quality': s.quality,
    'time_scale': s.time_scale,
    'gravity': list(scene.gravity),
    'mesh': {'object': obj.name, 'vertices': len(mesh.vertices), 'faces': len(mesh.polygons), 'components': len(components)},
    'pin_vertices': len(pin_ids),
    'free_vertices': len(mesh.vertices) - len(pin_ids),
    'pin_weight': 1.0,
    'cache': {
        'is_baked': bool(mod.point_cache.is_baked),
        'use_disk_cache': bool(mod.point_cache.use_disk_cache),
        'filepath': getattr(mod.point_cache, 'filepath', None),
        'files': len(cache_files),
        'bytes': sum(item['bytes'] for item in cache_files),
    },
    'collision': {'object': body.name, 'use_collision': c.use_collision, 'use_self_collision': c.use_self_collision, 'distance_min': c.distance_min, 'body_outer': body_col.thickness_outer, 'body_inner': body_col.thickness_inner},
    'samples': samples,
}
if armature is not None:
    identity = Matrix.Identity(4)
    posed_bones = []
    for bone in armature.pose.bones:
        delta = max(
            abs(bone.matrix_basis[row][col] - identity[row][col])
            for row in range(4) for col in range(4)
        )
        if delta > 1e-5:
            posed_bones.append(bone.name)
    manifest['pose'] = {
        'armature': armature.name,
        'posed_bones': len(posed_bones),
        'root_location': [float(value) for value in character_root.location] if character_root else None,
        'root_rotation': [float(value) for value in character_root.rotation_euler] if character_root else None,
    }
with open(manifest_path, 'w', encoding='utf-8') as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)
# Keep helpers for later editing, but remove the wire/bone overlay from the viewport.
body.hide_viewport = True
if armature is not None:
    armature.hide_viewport = True
for selected in bpy.context.selected_objects:
    selected.select_set(False)
bpy.context.view_layer.objects.active = None
scene.frame_set(120)
save_result = bpy.ops.wm.save_as_mainfile(filepath=final_blend, check_existing=False)
print('FINAL_SAVE|result=%s exists=%s path=%s' % (save_result, os.path.exists(final_blend), final_blend))
print(json.dumps(manifest, ensure_ascii=False, indent=2))
