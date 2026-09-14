import bpy
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
old_group = mod.settings.vertex_group_mass
old_end = mod.point_cache.frame_end
mod.settings.vertex_group_mass = ''
mod.point_cache.frame_end = 20
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
samples = []
for frame in [1, 5, 10, 20]:
    scene.frame_set(frame)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    center = sum((v.co for v in ev.data.vertices), Vector()) / len(ev.data.vertices)
    samples.append({'frame': frame, 'v0': list(ev.data.vertices[0].co), 'center': list(center)})
print('UNPINNED|' + str(samples))
# Restore the previous pin setup without saving this diagnostic state.
with bpy.context.temp_override(**override):
    bpy.ops.ptcache.free_bake_all()
mod.settings.vertex_group_mass = old_group
mod.point_cache.frame_end = old_end
scene.frame_set(1)
