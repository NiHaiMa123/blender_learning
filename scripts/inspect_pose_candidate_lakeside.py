import bpy
import json
from mathutils import Matrix

path = r'D:\software\blender\project\今汐_夜晚湖畔.blend'
bpy.ops.wm.open_mainfile(filepath=path)

scene = bpy.context.scene
source = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_mesh')
arm = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_arm')
empty = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311')
identity = Matrix.Identity(4)
posed = []
if arm:
    for bone in arm.pose.bones:
        delta = max(
            abs(bone.matrix_basis[row][col] - identity[row][col])
            for row in range(4) for col in range(4)
        )
        if delta > 1e-5:
            posed.append(bone.name)
action = arm.animation_data.action if arm and arm.animation_data else None
report = {
    'filepath': bpy.data.filepath,
    'frame': scene.frame_current,
    'frame_range': [scene.frame_start, scene.frame_end],
    'source_exists': source is not None,
    'source_hidden_viewport': source.hide_viewport if source else None,
    'source_hidden_render': source.hide_render if source else None,
    'source_vertices': len(source.data.vertices) if source else None,
    'source_modifiers': [modifier.type for modifier in source.modifiers] if source else None,
    'root_location': [round(float(value), 6) for value in empty.location] if empty else None,
    'root_rotation': [round(float(value), 6) for value in empty.rotation_euler] if empty else None,
    'armature_pose_position': arm.data.pose_position if arm else None,
    'posed_bones': len(posed),
    'posed_sample': posed[:30],
    'action': action.name if action else None,
    'action_range': [float(value) for value in action.frame_range] if action else None,
    'cloth_rebuild_objects': sorted(
        obj.name for obj in bpy.data.objects if obj.name.startswith('CLOTH_REBUILD_')
    ),
}
print('POSE_CANDIDATE|' + json.dumps(report, ensure_ascii=False))
