import bpy
import json
import math
import os
from mathutils import Vector

scene = bpy.context.scene
report = {}
report['blend'] = bpy.data.filepath
report['scene_frames'] = [scene.frame_start, scene.frame_end, scene.frame_current]

for name in ['CLOTH_REBUILD_SKIRT', 'CLOTH_REBUILD_BODY_COLLIDER', 'CLOTH_REBUILD_BODY_STATIC']:
    ob = bpy.data.objects.get(name)
    report[name] = {
        'exists': ob is not None,
        'hide_viewport': ob.hide_viewport if ob else None,
        'hide_render': ob.hide_render if ob else None,
        'verts': len(ob.data.vertices) if ob and ob.type == 'MESH' else None,
        'faces': len(ob.data.polygons) if ob and ob.type == 'MESH' else None,
    }

obj = bpy.data.objects.get('CLOTH_REBUILD_SKIRT')
if obj is not None:
    mod = obj.modifiers.get('CLOTH_REBUILD_SKIRT')
    report['cloth_modifier'] = {'exists': mod is not None, 'type': mod.type if mod else None}
    if mod is not None:
        s = mod.settings
        c = mod.collision_settings
        pc = mod.point_cache
        try:
            baked = pc.is_baked
        except Exception:
            baked = None
        report['cloth'] = {
            'quality': s.quality,
            'mass': s.mass,
            'time_scale': s.time_scale,
            'pin_group': s.vertex_group_mass,
            'use_collision': c.use_collision,
            'use_self_collision': c.use_self_collision,
            'cache_frames': [pc.frame_start, pc.frame_end, pc.frame_step],
            'use_disk_cache': pc.use_disk_cache,
            'is_baked': baked,
        }
    vg = obj.vertex_groups.get('CLOTH_PIN_WAIST')
    report['pin_group'] = {'exists': vg is not None}
    pin_ids = set()
    free_ids = set()
    if vg is not None:
        for vertex in obj.data.vertices:
            try:
                weight = vg.weight(vertex.index)
            except RuntimeError:
                weight = 0.0
            if weight >= 1.0 - 1e-6:
                pin_ids.add(vertex.index)
            else:
                free_ids.add(vertex.index)
        report['pin_group'].update({
            'pin_weight': 1.0,
            'pin_vertices': len(pin_ids),
            'free_vertices': len(free_ids),
        })
    report['materials'] = [m.name if m else None for m in obj.data.materials]

body = bpy.data.objects.get('CLOTH_REBUILD_BODY_COLLIDER')
if body is not None:
    bc = body.collision
    report['body_collision'] = {
        'use': bc.use,
        'thickness_outer': bc.thickness_outer,
        'thickness_inner': bc.thickness_inner,
        'damping': bc.damping,
    }

depsgraph = bpy.context.evaluated_depsgraph_get()
samples = []
bad_total = 0
base_coords = [vertex.co.copy() for vertex in obj.data.vertices]
for f in [1, 80, 120]:
    scene.frame_set(f)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    coords = [v.co for v in ev.data.vertices]
    bad = sum(1 for v in coords for x in v if not math.isfinite(x))
    bad_total += bad
    cx = sum(v[0] for v in coords) / len(coords)
    cy = sum(v[1] for v in coords) / len(coords)
    cz = sum(v[2] for v in coords) / len(coords)
    displacements = [
        (coords[index] - base_coords[index]).length
        for index in range(len(coords))
    ]
    pin_displacements = [displacements[index] for index in pin_ids]
    free_displacements = [displacements[index] for index in free_ids]
    samples.append({
        'frame': f,
        'center': [round(cx, 6), round(cy, 6), round(cz, 6)],
        'min': [round(min(v[0] for v in coords), 6), round(min(v[1] for v in coords), 6), round(min(v[2] for v in coords), 6)],
        'max': [round(max(v[0] for v in coords), 6), round(max(v[1] for v in coords), 6), round(max(v[2] for v in coords), 6)],
        'non_finite': bad,
        'pinned_max_displacement': round(max(pin_displacements), 8) if pin_displacements else None,
        'free_mean_displacement': round(sum(free_displacements) / len(free_displacements), 8) if free_displacements else None,
        'free_max_displacement': round(max(free_displacements), 8) if free_displacements else None,
    })
report['samples'] = samples
report['non_finite_total'] = bad_total
report['passed'] = bool(
    report.get('cloth_modifier', {}).get('type') == 'CLOTH'
    and report.get('cloth', {}).get('is_baked')
    and report.get('cloth', {}).get('use_collision')
    and report.get('pin_group', {}).get('pin_vertices', 0) > 0
    and report.get('pin_group', {}).get('free_vertices', 0) > 0
    and bad_total == 0
    and samples[-1]['pinned_max_displacement'] is not None
    and samples[-1]['pinned_max_displacement'] < 1e-4
    and samples[-1]['free_mean_displacement'] is not None
    and samples[-1]['free_mean_displacement'] > 1e-3
)

out = r'D:\project\blender_learning\validation\cloth_final_check.json'
with open(out, 'w', encoding='utf-8') as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)
print('VALIDATE|baked=%s non_finite=%s frames=%s' % (
    report.get('cloth', {}).get('is_baked'), bad_total, report['scene_frames']))
