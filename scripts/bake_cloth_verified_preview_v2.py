import bpy
import json
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
vg = obj.vertex_groups['CLOTH_PIN_WAIST']
all_ids = [v.index for v in obj.data.vertices]
max_z = max(v.co.z for v in obj.data.vertices)
pin_ids = [v.index for v in obj.data.vertices if v.co.z >= max_z - 0.12]
vg.remove(all_ids)
vg.add(pin_ids, 1.0, 'REPLACE')
mod.settings.vertex_group_mass = vg.name
mod.settings.quality = 3
mod.collision_settings.collision_quality = 2
mod.point_cache.use_disk_cache = False
mod.point_cache.frame_start = 1
mod.point_cache.frame_end = 80
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
def sample(frame):
    scene.frame_set(frame)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    center = sum((v.co for v in ev.data.vertices), Vector()) / len(ev.data.vertices)
    return {
        'frame': frame,
        'center': [round(float(x), 6) for x in center],
        'v0': [round(float(x), 6) for x in ev.data.vertices[0].co],
        'vlast': [round(float(x), 6) for x in ev.data.vertices[-1].co],
    }
samples = [sample(frame) for frame in [1, 20, 40, 60, 80]]
scene.frame_set(80)
bpy.ops.wm.save_as_mainfile(filepath=r'D:\software\blender\project\今汐_cloth_rebuild_preview_v2.blend', check_existing=False)
print(json.dumps({'baked': bool(mod.point_cache.is_baked), 'pin_count': len(pin_ids), 'samples': samples}, ensure_ascii=False, indent=2))
