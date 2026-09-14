import bpy
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
c = mod.collision_settings
c.use_self_collision = True
c.self_distance_min = 0.003
c.self_friction = 0.5
c.collision_quality = 2
mod.point_cache.use_disk_cache = False
mod.point_cache.frame_start = 1
mod.point_cache.frame_end = 30
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
for f in [1, 10, 20, 30]:
    scene.frame_set(f)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    coords = [v.co for v in ev.data.vertices]
    center = sum(coords, Vector()) / len(coords)
    mins = [min(v[i] for v in coords) for i in range(3)]
    maxs = [max(v[i] for v in coords) for i in range(3)]
    out.append({'f': f, 'center': [round(float(x), 4) for x in center], 'min': [round(float(x), 4) for x in mins], 'max': [round(float(x), 4) for x in maxs]})
print('SELF_COLLISION|' + str(out))
