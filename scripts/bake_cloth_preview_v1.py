import bpy
import json
from mathutils import Vector

scene = bpy.context.scene
cloth_obj = bpy.data.objects.get('CLOTH_REBUILD_SKIRT')
collider = bpy.data.objects.get('CLOTH_REBUILD_BODY_COLLIDER')
if cloth_obj is None:
    raise RuntimeError('CLOTH_REBUILD_SKIRT not found')
mod = cloth_obj.modifiers.get('CLOTH_REBUILD_SKIRT')
if mod is None:
    raise RuntimeError('CLOTH_REBUILD_SKIRT modifier not found')
mod.settings.quality = 3
mod.collision_settings.collision_quality = 2
cache = mod.point_cache
pin = cloth_obj.vertex_groups.get('CLOTH_PIN_WAIST')
if pin is None:
    raise RuntimeError('CLOTH_PIN_WAIST not found')
all_ids = [v.index for v in cloth_obj.data.vertices]
pin_ids = []
for v in cloth_obj.data.vertices:
    try:
        if pin.weight(v.index) >= 0.5:
            pin_ids.append(v.index)
    except Exception:
        pass
# Refresh the mass/pin group so the cloth dependency graph sees the rebuilt weights.
pin.remove(all_ids)
pin.add(pin_ids, 1.0, 'REPLACE')
mod.settings.vertex_group_mass = ''
mod.settings.vertex_group_mass = pin.name
cache.use_disk_cache = False
cache.frame_start = 1
cache.frame_end = 80
cache.frame_step = 1
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

def sample_frame(frame):
    scene.frame_set(frame)
    scene.view_layers[0].update()
    verts = cloth_obj.data.vertices
    center = sum((v.co for v in verts), Vector()) / len(verts)
    return {
        'frame': frame,
        'center': [round(float(x), 6) for x in center],
        'v0': [round(float(x), 6) for x in verts[0].co],
        'vlast': [round(float(x), 6) for x in verts[-1].co],
    }

samples = [sample_frame(f) for f in [1, 20, 40, 60, 80]]
result = {
    'cache_baked': bool(cache.is_baked),
    'quality': mod.settings.quality,
    'collision_quality': mod.collision_settings.collision_quality,
    'self_collision': bool(mod.collision_settings.use_self_collision),
    'samples': samples,
}
scene.frame_set(80)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\software\blender\project\今汐_cloth_rebuild_preview_v2.blend', check_existing=False)
print(json.dumps(result, ensure_ascii=False, indent=2))
