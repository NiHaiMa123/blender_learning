import bpy
import json
import math
from mathutils import Vector

final_blend = r'D:\software\blender\project\今汐_cloth_rebuild_final.blend'
bpy.ops.wm.open_mainfile(filepath=final_blend)

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
group = obj.vertex_groups[mod.settings.vertex_group_mass]
pin_ids = set()
for vertex in obj.data.vertices:
    try:
        if group.weight(vertex.index) >= 1.0 - 1e-6:
            pin_ids.add(vertex.index)
    except RuntimeError:
        pass
free_ids = set(range(len(obj.data.vertices))) - pin_ids
base = [vertex.co.copy() for vertex in obj.data.vertices]
depsgraph = bpy.context.evaluated_depsgraph_get()
samples = []
for frame in [1, 80, 120]:
    scene.frame_set(frame)
    depsgraph.update()
    evaluated = obj.evaluated_get(depsgraph)
    coords = [vertex.co.copy() for vertex in evaluated.data.vertices]
    displacements = [(coords[index] - base[index]).length for index in range(len(coords))]
    center = sum(coords, Vector()) / len(coords)
    samples.append({
        'frame': frame,
        'center': [round(float(value), 6) for value in center],
        'non_finite': sum(
            1 for coordinate in coords for value in coordinate if not math.isfinite(value)
        ),
        'pinned_max_displacement': round(max(displacements[index] for index in pin_ids), 8),
        'free_mean_displacement': round(
            sum(displacements[index] for index in free_ids) / len(free_ids), 8
        ),
    })

report = {
    'filepath': bpy.data.filepath,
    'cloth_modifier': mod.type,
    'baked': bool(mod.point_cache.is_baked),
    'disk_cache': bool(mod.point_cache.use_disk_cache),
    'cache_filepath': getattr(mod.point_cache, 'filepath', None),
    'pin_vertices': len(pin_ids),
    'free_vertices': len(free_ids),
    'visible_body': bpy.data.objects['CLOTH_REBUILD_BODY_STATIC'].visible_get(),
    'collider_hidden_viewport': bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER'].hide_viewport,
    'armature_hidden_viewport': bpy.data.objects['鸣潮_今汐_桃夭灼灼1.0311_arm'].hide_viewport,
    'root_location': [
        round(float(value), 6)
        for value in bpy.data.objects['鸣潮_今汐_桃夭灼灼1.0311'].location
    ],
    'root_rotation': [
        round(float(value), 6)
        for value in bpy.data.objects['鸣潮_今汐_桃夭灼灼1.0311'].rotation_euler
    ],
    'samples': samples,
}
report['passed'] = bool(
    report['filepath'] == final_blend
    and report['cloth_modifier'] == 'CLOTH'
    and report['baked']
    and report['disk_cache']
    and report['visible_body']
    and report['collider_hidden_viewport']
    and report['armature_hidden_viewport']
    and report['root_location'] == [1.0, -7.0, 0.0]
    and abs(report['root_rotation'][2] - 4.101524) < 1e-5
    and all(sample['non_finite'] == 0 for sample in samples)
    and samples[-1]['pinned_max_displacement'] < 1e-4
    and samples[-1]['free_mean_displacement'] > 1e-3
)
with open(
    r'D:\project\blender_learning\validation\cloth_final_reopen_check.json',
    'w',
    encoding='utf-8',
) as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)
print('REOPEN_VALIDATE|' + json.dumps(report, ensure_ascii=False))
