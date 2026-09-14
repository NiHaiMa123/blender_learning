import bpy
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
settings = mod.settings
collision = mod.collision_settings
vg = obj.vertex_groups['CLOTH_PIN_WAIST']
all_ids = [v.index for v in obj.data.vertices]
max_z = max(v.co.z for v in obj.data.vertices)
pin_ids = [v.index for v in obj.data.vertices if v.co.z >= max_z - 0.12]
vg.remove(all_ids)
vg.add(pin_ids, 1.0, 'REPLACE')
settings.vertex_group_mass = vg.name
settings.quality = 4
settings.mass = 0.3
settings.air_damping = 10.0
settings.tension_stiffness = 80.0
settings.compression_stiffness = 80.0
settings.shear_stiffness = 40.0
settings.bending_stiffness = 2.0
settings.tension_damping = 20.0
settings.compression_damping = 20.0
settings.shear_damping = 20.0
settings.bending_damping = 8.0
settings.time_scale = 0.65
collision.use_collision = True
collision.use_self_collision = False
collision.collision_quality = 2
collision.distance_min = 0.005
collision.self_distance_min = 0.005
collision.damping = 0.8
collision.friction = 1.0
collision.self_friction = 1.0
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
print('STABILITY|' + str(out))
