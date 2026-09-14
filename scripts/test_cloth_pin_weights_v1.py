import bpy
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
pc = mod.point_cache
vg = obj.vertex_groups.get('CLOTH_PIN_WAIST')
pin_ids = set()
for v in obj.data.vertices:
    try:
        if vg.weight(v.index) >= 0.5:
            pin_ids.add(v.index)
    except Exception:
        pass
all_ids = [v.index for v in obj.data.vertices]

def bake_and_sample(label):
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
    for frame in [1, 10, 20]:
        scene.frame_set(frame)
        depsgraph.update()
        ev = obj.evaluated_get(depsgraph)
        center = sum((v.co for v in ev.data.vertices), Vector()) / len(ev.data.vertices)
        samples.append((frame, tuple(round(float(x), 5) for x in ev.data.vertices[0].co), tuple(round(float(x), 5) for x in center)))
    return samples

# Case A: explicit 1 for the waist and 0 for every free vertex.
vg.remove(all_ids)
vg.add(all_ids, 0.0, 'REPLACE')
vg.add(list(pin_ids), 1.0, 'REPLACE')
case_a = bake_and_sample('explicit_free_zero')

# Case B: intentionally inverted weights, retained only as a regression comparison.
vg.remove(all_ids)
vg.add(all_ids, 1.0, 'REPLACE')
vg.add(list(pin_ids), 0.0, 'REPLACE')
case_b = bake_and_sample('explicit_pin_zero')
print('CASE_A|' + str(case_a))
print('CASE_B|' + str(case_b))

with bpy.context.temp_override(window=bpy.context.window, screen=bpy.context.window.screen):
    bpy.ops.ptcache.free_bake_all()
vg.remove(all_ids)
vg.add(list(pin_ids), 1.0, 'REPLACE')
mod.settings.vertex_group_mass = vg.name
pc.frame_end = 80
scene.frame_set(1)
