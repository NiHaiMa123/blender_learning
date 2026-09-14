import bpy, json
from mathutils import Matrix

arm = bpy.data.objects['卡提希娅_arm']
action = arm.animation_data.action if arm.animation_data else None
rows = []
identity = Matrix.Identity(4)
for pb in arm.pose.bones:
    delta = max(abs(a - b) for row_a, row_b in zip(pb.matrix_basis, identity) for a, b in zip(row_a, row_b))
    if delta > 1e-4:
        rows.append({
            'bone': pb.name,
            'delta': round(delta, 6),
            'location': [round(v, 5) for v in pb.location],
            'rotation_mode': pb.rotation_mode,
            'scale': [round(v, 5) for v in pb.scale],
        })
rows.sort(key=lambda x: x['delta'], reverse=True)
result = {
    'action': action.name if action else None,
    'action_frame_range': list(action.frame_range) if action else None,
    'nonidentity_count': len(rows),
    'top': rows[:40],
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
