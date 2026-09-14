import bpy
import json

scene = bpy.context.scene
names = [
    'CLOTH_REBUILD_SKIRT',
    'CLOTH_REBUILD_BODY_COLLIDER',
    'CLOTH_REBUILD_BODY_STATIC',
]
report = {
    'filepath': bpy.data.filepath,
    'frame_range': [scene.frame_start, scene.frame_end, scene.frame_current],
    'gravity': list(scene.gravity),
    'objects': {},
}

for name in names:
    obj = bpy.data.objects.get(name)
    report['objects'][name] = {
        'exists': obj is not None,
        'type': obj.type if obj else None,
        'verts': len(obj.data.vertices) if obj and obj.type == 'MESH' else None,
        'faces': len(obj.data.polygons) if obj and obj.type == 'MESH' else None,
    }

obj = bpy.data.objects.get('CLOTH_REBUILD_SKIRT')
if obj:
    mod = obj.modifiers.get('CLOTH_REBUILD_SKIRT')
    report['modifier'] = {
        'exists': mod is not None,
        'type': mod.type if mod else None,
    }
    if mod:
        pc = mod.point_cache
        report['cloth'] = {
            'quality': mod.settings.quality,
            'mass': mod.settings.mass,
            'time_scale': mod.settings.time_scale,
            'pin_group': mod.settings.vertex_group_mass,
            'collision': mod.collision_settings.use_collision,
            'self_collision': mod.collision_settings.use_self_collision,
            'cache': [pc.frame_start, pc.frame_end, pc.frame_step],
            'disk_cache': pc.use_disk_cache,
            'baked': pc.is_baked,
            'cache_filepath': getattr(pc, 'filepath', None),
        }
    vg = obj.vertex_groups.get('CLOTH_PIN_WAIST')
    if vg:
        counts = {'zero': 0, 'one': 0, 'mid': 0, 'missing': 0}
        z_by_bucket = {'zero': [], 'one': [], 'mid': []}
        for vert in obj.data.vertices:
            try:
                weight = vg.weight(vert.index)
            except RuntimeError:
                counts['missing'] += 1
                continue
            bucket = 'zero' if weight <= 1e-6 else 'one' if weight >= 1.0 - 1e-6 else 'mid'
            counts[bucket] += 1
            z_by_bucket[bucket].append(float(vert.co.z))
        report['pin_weights'] = counts
        report['pin_z_ranges'] = {
            key: [min(values), max(values)] if values else None
            for key, values in z_by_bucket.items()
        }

print('AUDIT_CLOTH_LIVE|' + json.dumps(report, ensure_ascii=False))
