import bpy
from collections import Counter

obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
s = mod.settings
c = mod.collision_settings
vg = obj.vertex_groups.get('CLOTH_PIN_WAIST')
weights = []
if vg:
    for v in obj.data.vertices:
        try:
            weights.append(vg.weight(v.index))
        except Exception:
            pass
print('OBJ|verts=%d faces=%d mods=%s' % (len(obj.data.vertices), len(obj.data.polygons), [(m.name, m.type, m.show_viewport, m.show_render) for m in obj.modifiers]))
print('PIN|name=%s count=%d min=%.3f max=%.3f' % (s.vertex_group_mass, len(weights), min(weights) if weights else -1, max(weights) if weights else -1))
print('SETTINGS|goal=%.3f spring=%.3f pin=%.3f mass=%.3f gravity=%.3f quality=%d' % (s.goal_default, s.goal_spring, s.pin_stiffness, s.mass, s.effector_weights.gravity, s.quality))
print('COLLISION|use=%s self=%s q=%d dist=%.4f selfdist=%.4f' % (c.use_collision, c.use_self_collision, c.collision_quality, c.distance_min, c.self_distance_min))
pc = mod.point_cache
print('CACHE|baked=%s baking=%s outdated=%s range=%d..%d file=%s' % (pc.is_baked, pc.is_baking, pc.is_outdated, pc.frame_start, pc.frame_end, pc.filepath))
scene = bpy.context.scene
depsgraph = bpy.context.evaluated_depsgraph_get()
for f in [1, 2, 10, 80]:
    scene.frame_set(f)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    print('EVAL|f=%d|mod_eval=%s|verts=%d|v0=%s' % (f, ev.is_evaluated, len(ev.data.vertices), tuple(round(x, 5) for x in ev.data.vertices[0].co)))
