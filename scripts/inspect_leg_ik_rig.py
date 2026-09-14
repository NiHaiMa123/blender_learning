import bpy, json

arm = bpy.data.objects['卡提希娅_arm']
names = [
    '全ての親', 'センター', 'グルーブ', '腰', '下半身',
    '足.R', 'ひざ.R', '足首.R', '足D.R', 'ひざD.R', '足首D.R', '足先EX.R', 'つま先.R',
    '足IK親.R', '足ＩＫ.R', '足ＩＫ先.R', 'つま先ＩＫ.R', 'つま先ＩＫ先.R',
    '足.L', 'ひざ.L', '足首.L', '足D.L', 'ひざD.L', '足首D.L', '足先EX.L', 'つま先.L',
    '足IK親.L', '足ＩＫ.L', '足ＩＫ先.L', 'つま先ＩＫ.L', 'つま先ＩＫ先.L',
]

def vec(v):
    return [round(float(x), 6) for x in v]

def constraint_info(c):
    d = {
        'name': c.name,
        'type': c.type,
        'influence': c.influence,
        'mute': c.mute,
    }
    for attr in ('target', 'subtarget', 'pole_target', 'pole_subtarget', 'chain_count', 'pole_angle', 'use_tail', 'iterations'):
        if hasattr(c, attr):
            value = getattr(c, attr)
            if attr in ('target', 'pole_target'):
                value = value.name if value else None
            d[attr] = value
    return d

rows = []
for name in names:
    b = arm.data.bones.get(name)
    pb = arm.pose.bones.get(name)
    if not b or not pb:
        rows.append({'name': name, 'missing': True})
        continue
    rows.append({
        'name': name,
        'parent': b.parent.name if b.parent else None,
        'children': [c.name for c in b.children],
        'use_connect': b.use_connect,
        'head_local': vec(b.head_local),
        'tail_local': vec(b.tail_local),
        'length': round(b.length, 6),
        'collections': [c.name for c in b.collections],
        'rotation_mode': pb.rotation_mode,
        'lock_location': list(pb.lock_location),
        'lock_rotation': list(pb.lock_rotation),
        'constraints': [constraint_info(c) for c in pb.constraints],
    })

result = {
    'armature': arm.name,
    'pose_position': arm.data.pose_position,
    'bones': rows,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
