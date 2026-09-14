import bpy
import json
from mathutils import Vector


def bone_pose_summary(arm):
    items = []
    for pb in arm.pose.bones:
        changed = (
            pb.location.length > 1e-6
            or abs(pb.rotation_quaternion.w - 1.0) > 1e-6
            or Vector((pb.rotation_quaternion.x, pb.rotation_quaternion.y, pb.rotation_quaternion.z)).length > 1e-6
            or (pb.scale - Vector((1, 1, 1))).length > 1e-6
        )
        if changed and (any(s in pb.name for s in ['手', '指', '腕', 'ひじ', '肩']) or len(items) < 10):
            items.append({
                'name': pb.name,
                'location': list(pb.location),
                'rotation_mode': pb.rotation_mode,
                'rotation_quaternion': list(pb.rotation_quaternion),
                'rotation_euler': list(pb.rotation_euler),
                'scale': list(pb.scale),
            })
    return items


def rig_summary(name):
    arm = bpy.data.objects[name]
    names = ['手首.L', '人指１.L', '人指２.L', '人指３.L', '親指０.L', '親指１.L', '親指２.L', '手首.R', '人指１.R', '人指２.R', '人指３.R']
    bones = {}
    for n in names:
        b = arm.data.bones.get(n)
        p = arm.pose.bones.get(n)
        if b and p:
            bones[n] = {
                'rest_head': list(b.head_local),
                'rest_tail': list(b.tail_local),
                'pose_head': list(p.head),
                'pose_tail': list(p.tail),
                'rotation_mode': p.rotation_mode,
                'rotation_quaternion': list(p.rotation_quaternion),
                'rotation_euler': list(p.rotation_euler),
            }
    return {
        'name': name,
        'matrix_world': [list(row) for row in arm.matrix_world],
        'bones': bones,
        'changed_pose_bones': bone_pose_summary(arm),
    }


out = {
    'file': bpy.data.filepath,
    'source_rig': rig_summary('达妮娅_红色毛茸袖形态_arm'),
    'target_rig': rig_summary('达妮娅_arm'),
}
for n in ['左手套', '右手套']:
    o = bpy.data.objects[n]
    out[n] = {
        'matrix_world': [list(row) for row in o.matrix_world],
        'parent': o.parent.name if o.parent else None,
        'active_modifier': [(m.name, m.type, getattr(getattr(m, 'object', None), 'name', None)) for m in o.modifiers],
        'shape_keys': len(o.data.shape_keys.key_blocks) if o.data.shape_keys else 0,
    }
print(json.dumps(out, ensure_ascii=False, indent=2))
