import bpy, os, json
from mathutils import Matrix

scene = bpy.data.scenes['Codex_Cycles_Render']
arm = bpy.data.objects['卡提希娅_arm']

for obj in bpy.context.view_layer.objects:
    obj.select_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if arm.mode == 'POSE':
    bpy.ops.object.mode_set(mode='OBJECT')

arm.animation_data_create()
old_action = arm.animation_data.action
if old_action:
    old_action.name = '卡提希娅_参考姿势_备份'
arm.animation_data.action = None
for track in arm.animation_data.nla_tracks:
    track.mute = True

scene.frame_set(1)
for pb in arm.pose.bones:
    pb.location = (0.0, 0.0, 0.0)
    pb.scale = (1.0, 1.0, 1.0)
    pb.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
    pb.rotation_euler = (0.0, 0.0, 0.0)
    pb.rotation_axis_angle = (0.0, 0.0, 1.0, 0.0)
    pb.matrix_basis = Matrix.Identity(4)

bpy.context.view_layer.update()

new_action = bpy.data.actions.new('卡提希娅_新动作')
arm.animation_data.action = new_action
bpy.ops.object.mode_set(mode='POSE')

identity = Matrix.Identity(4)
max_delta = 0.0
nonidentity = []
for pb in arm.pose.bones:
    delta = max(abs(a - b) for row_a, row_b in zip(pb.matrix_basis, identity) for a, b in zip(row_a, row_b))
    max_delta = max(max_delta, delta)
    if delta > 1e-5:
        nonidentity.append(pb.name)

path = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)

result = {
    'old_action_backup': old_action.name if old_action else None,
    'new_action': new_action.name,
    'max_pose_basis_delta': max_delta,
    'nonidentity_bones': nonidentity,
    'saved': path,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
