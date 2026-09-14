import bpy
import json
from mathutils import Matrix

backup = r'D:\software\blender\project\今汐_before_cloth_rebuild.blend'
bpy.ops.wm.open_mainfile(filepath=backup)

scene = bpy.context.scene
identity = Matrix.Identity(4)
armatures = []
for obj in bpy.data.objects:
    if obj.type != 'ARMATURE':
        continue
    changed = []
    for bone in obj.pose.bones:
        delta = max(abs(bone.matrix_basis[row][col] - identity[row][col]) for row in range(4) for col in range(4))
        if delta > 1e-5:
            changed.append({
                'name': bone.name,
                'delta': round(float(delta), 6),
                'location': [round(float(value), 5) for value in bone.location],
                'rotation_mode': bone.rotation_mode,
            })
    action = obj.animation_data.action if obj.animation_data else None
    armatures.append({
        'name': obj.name,
        'location': [round(float(value), 5) for value in obj.location],
        'rotation': [round(float(value), 5) for value in obj.rotation_euler],
        'scale': [round(float(value), 5) for value in obj.scale],
        'pose_position': obj.data.pose_position,
        'action': action.name if action else None,
        'action_range': [float(value) for value in action.frame_range] if action else None,
        'posed_bones': len(changed),
        'posed_sample': changed[:30],
    })

source = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_mesh')
report = {
    'filepath': bpy.data.filepath,
    'frame': scene.frame_current,
    'frame_range': [scene.frame_start, scene.frame_end],
    'camera': scene.camera.name if scene.camera else None,
    'source': {
        'exists': source is not None,
        'hidden_viewport': source.hide_viewport if source else None,
        'hidden_render': source.hide_render if source else None,
        'modifiers': [
            {
                'name': modifier.name,
                'type': modifier.type,
                'object': modifier.object.name if hasattr(modifier, 'object') and modifier.object else None,
            }
            for modifier in source.modifiers
        ] if source else None,
    },
    'armatures': armatures,
}
print('POSE_BACKUP|' + json.dumps(report, ensure_ascii=False))
