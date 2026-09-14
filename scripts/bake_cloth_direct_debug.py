import bpy
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
pin = obj.vertex_groups['CLOTH_PIN_WAIST']
ids = [v.index for v in obj.data.vertices]
pin_ids = []
for v in obj.data.vertices:
    try:
        if pin.weight(v.index) >= 0.5:
            pin_ids.append(v.index)
    except Exception:
        pass
pin.remove(ids)
pin.add(pin_ids, 1.0, 'REPLACE')
mod.settings.vertex_group_mass = pin.name
mod.settings.quality = 3
mod.collision_settings.collision_quality = 2
mod.point_cache.use_disk_cache = False
mod.point_cache.frame_start = 1
mod.point_cache.frame_end = 20
scene.frame_set(1)
bpy.context.view_layer.update()
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
for f in [1, 5, 10, 20]:
    scene.frame_set(f)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    center = sum((v.co for v in ev.data.vertices), Vector()) / len(ev.data.vertices)
    out.append((f, tuple(round(float(x), 5) for x in ev.data.vertices[0].co), tuple(round(float(x), 5) for x in center)))
print('DIRECT|' + str(out))
print('CACHE|baked=%s range=%d..%d' % (mod.point_cache.is_baked, mod.point_cache.frame_start, mod.point_cache.frame_end))
