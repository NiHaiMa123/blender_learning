import bpy, math, os, json
from mathutils import Vector, Matrix

scene = bpy.data.scenes['Codex_Cycles_Render']
arm = bpy.data.objects['卡提希娅_arm']
backup = r'D:\project\blender_learning\renders\before_native_leg_pole_ik.blend'
output = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
os.makedirs(os.path.dirname(backup), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True, check_existing=False)

for obj in bpy.context.view_layer.objects:
    obj.select_set(False)
arm.hide_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

if arm.mode != 'POSE':
    bpy.ops.object.mode_set(mode='POSE')

# Preserve every current pose transform while the rig is structurally edited.
pose_snapshot = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
baseline_eval = {
    name: arm.pose.bones[name].matrix.copy()
    for name in ('足.R', 'ひざ.R', '足首.R', '足.L', 'ひざ.L', '足首.L', '下半身', '腰')
}

bpy.ops.object.mode_set(mode='EDIT')
edit_bones = arm.data.edit_bones
root_parent = edit_bones.get('全ての親')
created = []
for side in ('R', 'L'):
    pole_name = f'膝盖朝向.{side}'
    knee = edit_bones[f'ひざ.{side}']
    pole = edit_bones.get(pole_name)
    if pole is None:
        pole = edit_bones.new(pole_name)
        created.append(pole_name)
    # Model front is -Y.  Keep the pole well ahead of the knee so the solver
    # remains stable during large foot translations.
    pole.head = knee.head + Vector((0.0, -0.42, 0.0))
    pole.tail = pole.head + Vector((0.0, 0.0, 0.12))
    pole.parent = root_parent
    pole.use_connect = False
    pole.use_deform = False

bpy.ops.object.mode_set(mode='POSE')

ik_collection = arm.data.collections.get('【主控】脚部IK')
if ik_collection is None:
    raise RuntimeError('Existing foot IK bone collection not found')

for side in ('R', 'L'):
    pole_name = f'膝盖朝向.{side}'
    ik_collection.assign(arm.data.bones[pole_name])
    pole_pb = arm.pose.bones[pole_name]
    pole_pb.rotation_mode = 'QUATERNION'
    pole_pb.lock_location = (False, False, False)
    pole_pb.lock_rotation = (True, True, True)
    pole_pb.lock_rotation_w = True
    pole_pb.lock_scale = (True, True, True)

# Restore the exact pose state saved before edit mode.
for name, matrix_basis in pose_snapshot.items():
    if name in arm.pose.bones:
        arm.pose.bones[name].matrix_basis = matrix_basis
bpy.context.view_layer.update()

def leg_ik_constraint(side):
    knee_pb = arm.pose.bones[f'ひざ.{side}']
    target_name = f'足ＩＫ.{side}'
    candidates = [
        c for c in knee_pb.constraints
        if c.type == 'IK' and c.target == arm and c.subtarget == target_name and c.chain_count == 2
    ]
    if not candidates:
        raise RuntimeError(f'Existing leg IK constraint missing for {side}')
    return candidates[0]

constraints = {}
for side in ('R', 'L'):
    c = leg_ik_constraint(side)
    c.name = '原生腿部IK（含膝盖朝向）'
    c.target = arm
    c.subtarget = f'足ＩＫ.{side}'
    c.chain_count = 2
    c.pole_target = arm
    c.pole_subtarget = f'膝盖朝向.{side}'
    c.influence = 1.0
    c.mute = False
    if hasattr(c, 'use_rotation'):
        c.use_rotation = False
    constraints[side] = c

def matrix_error(a, b):
    return sum((a[r][c] - b[r][c]) ** 2 for r in range(4) for c in range(4))

# Determine the correct pole angle from the existing rest orientation rather
# than assuming a generic bone roll.  Choose the angle that changes the
# already-valid imported leg pose the least.
chosen_angles = {}
for side in ('R', 'L'):
    c = constraints[side]
    names = (f'足.{side}', f'ひざ.{side}', f'足首.{side}')
    best = None
    for degree in range(-180, 181, 2):
        angle = math.radians(degree)
        c.pole_angle = angle
        bpy.context.view_layer.update()
        error = sum(matrix_error(arm.pose.bones[n].matrix, baseline_eval[n]) for n in names)
        if best is None or error < best[0]:
            best = (error, angle, degree)
    c.pole_angle = best[1]
    chosen_angles[side] = {'degrees': best[2], 'rest_error': best[0]}
    bpy.context.view_layer.update()

# Re-enable the renamed existing control collection for direct Pose Mode use.
ik_collection.is_visible = True

def pose_matrix_delta(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))

def perform_test(side, delta, rotation_degrees):
    # Restore all user transforms before each independent side test.
    for name, matrix_basis in pose_snapshot.items():
        if name in arm.pose.bones:
            arm.pose.bones[name].matrix_basis = matrix_basis
    bpy.context.view_layer.update()

    ik = arm.pose.bones[f'足ＩＫ.{side}']
    original_matrix = ik.matrix.copy()
    moved = original_matrix.copy()
    moved.translation += Vector(delta)
    pos = moved.translation.copy()
    rotation = Matrix.Rotation(math.radians(rotation_degrees), 4, 'Z')
    moved = Matrix.Translation(pos) @ rotation @ Matrix.Translation(-pos) @ moved
    ik.matrix = moved
    bpy.context.view_layer.update()

    thigh = arm.pose.bones[f'足.{side}']
    knee = arm.pose.bones[f'ひざ.{side}']
    ankle = arm.pose.bones[f'足首.{side}']
    pole = arm.pose.bones[f'膝盖朝向.{side}']
    toe_ik = arm.pose.bones[f'つま先ＩＫ.{side}']

    hip = thigh.head.copy()
    joint = knee.head.copy()
    foot = ankle.head.copy()
    axis = foot - hip
    t = (joint - hip).dot(axis) / max(axis.length_squared, 1e-12)
    projected = hip + axis * t
    bend = joint - projected
    pole_direction = pole.head - projected
    pole_alignment = bend.normalized().dot(pole_direction.normalized()) if bend.length > 1e-8 else 0.0
    ankle_target_error = (ankle.head - ik.head).length
    foot_direction = (ankle.tail - ankle.head).normalized()
    target_direction = (toe_ik.head - ankle.head).normalized()
    foot_alignment = foot_direction.dot(target_direction)

    other = 'L' if side == 'R' else 'R'
    other_delta = max(
        pose_matrix_delta(arm.pose.bones[f'{name}.{other}'].matrix, baseline_eval[f'{name}.{other}'])
        for name in ('足', 'ひざ', '足首')
    )
    pelvis_delta = max(
        pose_matrix_delta(arm.pose.bones[name].matrix, baseline_eval[name])
        for name in ('下半身', '腰')
    )
    return {
        'ankle_target_error': ankle_target_error,
        'pole_alignment': pole_alignment,
        'knee_bend_amount': bend.length,
        'foot_rotation_alignment': foot_alignment,
        'opposite_leg_delta': other_delta,
        'pelvis_delta': pelvis_delta,
        'knee_position': list(joint),
        'ankle_position': list(foot),
    }

tests = {
    'R': perform_test('R', (-0.05, -0.16, 0.18), -18.0),
    'L': perform_test('L', (0.06, -0.12, 0.14), 16.0),
}

# Restore the user's starting pose after testing; IK remains configured.
for name, matrix_basis in pose_snapshot.items():
    if name in arm.pose.bones:
        arm.pose.bones[name].matrix_basis = matrix_basis
bpy.context.view_layer.update()

for area in bpy.context.window.screen.areas:
    area.tag_redraw()

bpy.ops.wm.save_as_mainfile(filepath=output, copy=True, check_existing=False)
result = {
    'created_poles': created,
    'reused_foot_controls': ['足ＩＫ.R', '足ＩＫ.L'],
    'pole_angles': chosen_angles,
    'tests': tests,
    'saved': output,
    'backup': backup,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
