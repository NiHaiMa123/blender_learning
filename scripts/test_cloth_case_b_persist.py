import bpy
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
vg = obj.vertex_groups['CLOTH_PIN_WAIST']
all_ids = [v.index for v in obj.data.vertices]
max_z = max(v.co.z for v in obj.data.vertices)
old_pin = [v.index for v in obj.data.vertices if v.co.z >= max_z - 0.12]
vg.remove(all_ids)
vg.add(old_pin, 1.0, 'REPLACE')
free_sample = next((i for i in all_ids if i not in set(old_pin)), None)
pin_sample = old_pin[0] if old_pin else None
print('WEIGHTS|free_index=%s free_weight=%s pin_index=%s pin_weight=%s' % (
    free_sample, 0.0,
    pin_sample, vg.weight(pin_sample) if pin_sample is not None else None))
mod.settings.vertex_group_mass = vg.name
mod.point_cache.use_disk_cache = False
mod.point_cache.frame_start = 1
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
out = []
for f in [1, 10, 20]:
    scene.frame_set(f)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    center = sum((v.co for v in ev.data.vertices), Vector()) / len(ev.data.vertices)
    out.append((f, tuple(round(float(x), 5) for x in ev.data.vertices[0].co), tuple(round(float(x), 5) for x in center)))
print('RESULT|' + str(out))
