import bpy
from collections import defaultdict, deque
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
settings = mod.settings
cloth_col = mod.collision_settings
body_col = bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER'].collision
mesh = obj.data

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
ids = [v.index for v in mesh.vertices]
vg.remove(ids)
vg.add(pin_ids, 1.0, 'REPLACE')
settings.vertex_group_mass = vg.name

body_col.use = True
body_col.use_culling = False
body_col.use_normal = False
body_col.thickness_outer = 0.02
body_col.thickness_inner = 0.02
body_col.damping = 0.6
settings.quality = 5
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
settings.time_scale = 0.5
cloth_col.use_collision = True
cloth_col.use_self_collision = True
cloth_col.collision_quality = 2
cloth_col.distance_min = 0.004
cloth_col.self_distance_min = 0.003
cloth_col.damping = 0.9
cloth_col.friction = 0.5
cloth_col.self_friction = 0.5
mod.point_cache.use_disk_cache = False
mod.point_cache.frame_start = 1
mod.point_cache.frame_end = 40
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
out = []
for f in [1, 10, 20, 30, 40]:
    scene.frame_set(f)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    coords = [v.co for v in ev.data.vertices]
    center = sum(coords, Vector()) / len(coords)
    mins = [min(v[i] for v in coords) for i in range(3)]
    maxs = [max(v[i] for v in coords) for i in range(3)]
    out.append({'f': f, 'center': [round(float(x), 4) for x in center], 'min': [round(float(x), 4) for x in mins], 'max': [round(float(x), 4) for x in maxs]})
print('OUTER_SELF|verts=%d faces=%d comps=%d pins=%d result=%s' % (len(mesh.vertices), len(mesh.polygons), len(components), len(pin_ids), out))
