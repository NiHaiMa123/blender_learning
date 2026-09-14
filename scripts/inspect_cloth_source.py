import bpy
import json
from collections import Counter

mesh = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_mesh')
arm = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_arm')
print('FILE|' + bpy.data.filepath)
print('MESH|' + str(mesh.name if mesh else None))
if mesh:
    print('MESH_XFORM|loc=%s rot=%s scale=%s' % (tuple(round(x, 4) for x in mesh.location), tuple(round(x, 4) for x in mesh.rotation_euler), tuple(round(x, 4) for x in mesh.scale)))
    print('MESH_COUNTS|verts=%d edges=%d polys=%d mats=%d groups=%d shape_keys=%d' % (len(mesh.data.vertices), len(mesh.data.edges), len(mesh.data.polygons), len(mesh.data.materials), len(mesh.vertex_groups), len(mesh.data.shape_keys.key_blocks) if mesh.data.shape_keys else 0))
    print('MESH_MODS|' + str([(m.name, m.type, getattr(m, 'show_viewport', None), getattr(m, 'show_render', None)) for m in mesh.modifiers]))
    print('MATS:')
    for i, m in enumerate(mesh.data.materials):
        faces = sum(1 for p in mesh.data.polygons if p.material_index == i)
        print('MAT|%03d|faces=%d|%s' % (i, faces, m.name if m else None))
    print('GROUPS_SAMPLE|' + ','.join(vg.name for vg in mesh.vertex_groups[:80]))
    print('GROUPS_CLOTH:')
    for vg in mesh.vertex_groups:
        n = vg.name
        if any(k in n for k in ['裙', '袖', '上半身', '下半身', '骨盆', '髪', 'Hair', 'Piao', '带', '辫']):
            print('VG|' + n)
    # Material neighborhoods: list unique material IDs per connected component.
    print('POLY_BOUNDS_BY_MAT:')
    for i, m in enumerate(mesh.data.materials):
        polys = [p for p in mesh.data.polygons if p.material_index == i]
        if not polys:
            continue
        verts = sorted(set(v for p in polys for v in p.vertices))
        zs = [mesh.data.vertices[v].co.z for v in verts]
        print('BOUND|%03d|%s|faces=%d|verts=%d|z=%.4f..%.4f' % (i, m.name if m else None, len(polys), len(verts), min(zs), max(zs)))
print('ARM|' + str(arm.name if arm else None))
if arm:
    print('ARM_XFORM|loc=%s rot=%s scale=%s' % (tuple(round(x, 4) for x in arm.location), tuple(round(x, 4) for x in arm.rotation_euler), tuple(round(x, 4) for x in arm.scale)))
    print('ARM_MODS|' + str([(m.name, m.type, getattr(m, 'object', None).name if getattr(m, 'object', None) else None) for m in arm.modifiers]))
    print('ARM_COLLECTIONS|' + str([(c.name, len(c.bones), c.is_visible) for c in arm.data.collections]))
print('SCENE|frame=%d..%d current=%d gravity=%s units=%s scale=%.4f' % (bpy.context.scene.frame_start, bpy.context.scene.frame_end, bpy.context.scene.frame_current, tuple(bpy.context.scene.gravity), bpy.context.scene.unit_settings.system, bpy.context.scene.unit_settings.scale_length))
