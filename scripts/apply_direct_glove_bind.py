import bpy
import json
import math
from pathlib import Path
from mathutils import Matrix, Quaternion


SOURCE_FILE = 'D:/project/blender_learning/达妮娅_鞋子变形修复_手套绑定前备份_20260909_193757.blend'
OUT_FILE = 'D:/project/blender_learning/达妮娅_鞋子变形修复_手套直接骨骼绑定_手臂保留_当前姿势保持_20260909.blend'
ROOT = Path('D:/project/blender_learning/validation/glove_direct_bind_full_hand_20260909')
ROOT.mkdir(parents=True, exist_ok=True)

source = bpy.data.objects['达妮娅_红色毛茸袖形态_arm']
target = bpy.data.objects['达妮娅_arm']
body = bpy.data.objects['达妮娅_mesh']

# Make a complete pre-change copy without changing the user's source file.
before_file = ROOT / 'before_direct_glove_bind.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(before_file), copy=True)


def deform_matrix(armature, bone_name):
    bone = armature.data.bones.get(bone_name)
    pose_bone = armature.pose.bones.get(bone_name)
    if bone is None or pose_bone is None:
        return None
    return (
        armature.matrix_world
        @ pose_bone.matrix
        @ bone.matrix_local.inverted()
        @ armature.matrix_world.inverted()
    )


def weighted_deform_matrix(obj, vertex, armature):
    matrix = Matrix.Identity(4) * 0.0
    total = 0.0
    for item in vertex.groups:
        group_name = obj.vertex_groups[item.group].name
        bone_matrix = deform_matrix(armature, group_name)
        if bone_matrix is not None:
            matrix += item.weight * bone_matrix
            total += item.weight
    if total > 1.0:
        matrix *= 1.0 / total
    else:
        matrix += Matrix.Identity(4) * (1.0 - total)
    return matrix


def evaluated_world_vertices(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    return [evaluated.matrix_world @ vertex.co for vertex in evaluated.data.vertices]


def pose_snapshot(armature, names):
    result = {}
    for name in names:
        pose_bone = armature.pose.bones.get(name)
        if pose_bone is None:
            continue
        result[name] = {
            'location': pose_bone.location.copy(),
            'rotation_mode': pose_bone.rotation_mode,
            'rotation_quaternion': pose_bone.rotation_quaternion.copy(),
            'rotation_euler': pose_bone.rotation_euler.copy(),
            'rotation_axis_angle': pose_bone.rotation_axis_angle[:],
            'scale': pose_bone.scale.copy(),
        }
    return result


def restore_pose(armature, snapshot):
    for name, values in snapshot.items():
        pose_bone = armature.pose.bones[name]
        pose_bone.location = values['location']
        pose_bone.rotation_mode = values['rotation_mode']
        pose_bone.rotation_quaternion = values['rotation_quaternion']
        pose_bone.rotation_euler = values['rotation_euler']
        pose_bone.rotation_axis_angle = values['rotation_axis_angle']
        pose_bone.scale = values['scale']


report = {
    'source_file': SOURCE_FILE,
    'output_file': OUT_FILE,
    'objects': {},
}

# Capture the exact current fitted result before touching either glove.
initial_world = {}
for name in ['左手套', '右手套']:
    glove = bpy.data.objects[name]
    initial_world[name] = glove.matrix_world.copy()
    initial_world[name + '_evaluated'] = evaluated_world_vertices(glove)

# Bake each glove from the source rig into a target-rig rest mesh. The inverse
# of the target rig's CURRENT pose is used, so the visible fitted position is
# preserved at the moment of binding. Every shape-key block is calibrated too.
for name in ['左手套', '右手套']:
    glove = bpy.data.objects[name]
    old_world = glove.matrix_world.copy()
    old_world_inverse = old_world.inverted_safe()
    vertex_count = len(glove.data.vertices)

    for vertex_index, vertex in enumerate(glove.data.vertices):
        source_matrix = weighted_deform_matrix(glove, vertex, source)
        target_matrix = weighted_deform_matrix(glove, vertex, target)
        target_inverse = target_matrix.inverted_safe()

        if glove.data.shape_keys:
            for key in glove.data.shape_keys.key_blocks:
                source_rest_world = old_world @ key.data[vertex_index].co
                source_current_world = source_matrix @ source_rest_world
                target_rest_world = target_inverse @ source_current_world
                key.data[vertex_index].co = old_world_inverse @ target_rest_world
            glove.data.vertices[vertex_index].co = glove.data.shape_keys.key_blocks['Basis'].data[vertex_index].co
        else:
            source_current_world = initial_world[name + '_evaluated'][vertex_index]
            target_rest_world = target_inverse @ source_current_world
            glove.data.vertices[vertex_index].co = old_world_inverse @ target_rest_world

    for modifier in list(glove.modifiers):
        glove.modifiers.remove(modifier)
    glove.parent = target
    glove.matrix_world = old_world
    armature_modifier = glove.modifiers.new('手套直接跟随素体骨骼_保持当前姿势', 'ARMATURE')
    armature_modifier.object = target
    armature_modifier.use_deform_preserve_volume = False
    glove['绑定方式'] = '当前姿势校准后直接使用达妮娅_arm逐指骨骼权重'
    report['objects'][name] = {
        'vertices': vertex_count,
        'shape_keys_preserved': len(glove.data.shape_keys.key_blocks) if glove.data.shape_keys else 0,
        'armature': target.name,
    }

bpy.context.view_layer.update()

# Confirm that binding did not move either glove in the current pose.
for name in ['左手套', '右手套']:
    actual = evaluated_world_vertices(bpy.data.objects[name])
    desired = initial_world[name + '_evaluated']
    report['objects'][name]['current_pose_max_error'] = max(
        (actual[i] - desired[i]).length for i in range(len(desired))
    )

# Build a narrow, reversible mask for only the hand skin/nail region. The
# cutoff is above the wrist so the arms and forearms remain visible.
mask_group_name = '手套穿戴_内部皮肤与指甲'
mask_group = body.vertex_groups.get(mask_group_name) or body.vertex_groups.new(name=mask_group_name)
mask_ids = set()
for side in ['L', 'R']:
    wrist = target.data.bones['手首.' + side]
    axis = (wrist.tail_local - wrist.head_local).normalized()
    sign = 1 if side == 'L' else -1
    hand_bone_names = [
        f'手首.{side}', f'手捩.{side}', f'手捩1.{side}', f'ダミー.{side}',
        f'親指０.{side}', f'親指１.{side}', f'親指２.{side}',
    ]
    for finger in ['人指', '中指', '薬指', '小指']:
        hand_bone_names.extend(f'{finger}{joint}.{side}' for joint in ['１', '２', '３'])
    hand_group_indices = {
        body.vertex_groups[name].index
        for name in hand_bone_names
        if body.vertex_groups.get(name)
    }
    # Use bone weights rather than material slots so every visible hand
    # surface and nail is hidden, while the upper arm stays untouched.
    for vertex in body.data.vertices:
        has_hand_weight = any(
            item.group in hand_group_indices and item.weight > 0.001
            for item in vertex.groups
        )
        in_hand_region = (
            sign * vertex.co.x > 0.25
            and 0.70 < vertex.co.z < 1.20
            and (vertex.co - wrist.head_local).dot(axis) > -0.08
        )
        if has_hand_weight and in_hand_region:
            mask_ids.add(vertex.index)
mask_group.add(sorted(mask_ids), 1.0, 'REPLACE')

old_mask = body.modifiers.get('穿戴手套_隐藏内部手部')
if old_mask:
    body.modifiers.remove(old_mask)
mask = body.modifiers.new('穿戴手套_隐藏内部手部', 'MASK')
mask.vertex_group = mask_group.name
mask.invert_vertex_group = True
mask.show_viewport = True
mask.show_render = True
target['穿戴手套'] = 1.0
source.hide_set(True)
source.hide_viewport = True
source.hide_render = True
report['body_mask'] = {
    'vertex_group': mask_group.name,
    'masked_vertices': len(mask_ids),
    'arms_kept': True,
    'reversible_modifier': mask.name,
    'selection_method': 'all hand/nail surfaces with hand/finger bone weights; arm region excluded',
}

bpy.context.view_layer.update()
body_eval = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
report['body_mask']['evaluated_vertices_after_mask'] = len(body_eval.data.vertices)

# Test independent index-finger motion, then restore the exact pose.
finger_names = ['人指１.L', '人指１.R']
finger_pose = pose_snapshot(target, finger_names)
before_motion = {name: evaluated_world_vertices(bpy.data.objects[name]) for name in ['左手套', '右手套']}
for name in finger_names:
    pose_bone = target.pose.bones.get(name)
    if pose_bone:
        pose_bone.rotation_mode = 'QUATERNION'
        pose_bone.rotation_quaternion = pose_bone.rotation_quaternion @ Quaternion((1, 0, 0), math.radians(15))
bpy.context.view_layer.update()
after_motion = {name: evaluated_world_vertices(bpy.data.objects[name]) for name in ['左手套', '右手套']}
report['finger_test_15deg'] = {
    name: max((after_motion[name][i] - before_motion[name][i]).length for i in range(len(before_motion[name])))
    for name in ['左手套', '右手套']
}
restore_pose(target, finger_pose)
bpy.context.view_layer.update()

for name in ['左手套', '右手套']:
    restored = evaluated_world_vertices(bpy.data.objects[name])
    baseline = initial_world[name + '_evaluated']
    report['objects'][name]['restored_pose_max_error'] = max(
        (restored[i] - baseline[i]).length for i in range(len(baseline))
    )

# Put the reversible instructions into the .blend itself.
notes = '''手套直接骨骼绑定（当前姿势保持）

- 左右手套已从红色形态骨架转为达妮娅_arm直接驱动。
- 绑定前使用当前姿势校准，所以绑定瞬间手套位置不跳。
- 手指权重按人指、中指、药指、小指和拇指分开，测试单独转动食指可跟随。
- 达妮娅_mesh上的“穿戴手套_隐藏内部手部”只隐藏手套内部皮肤与指甲，手臂保留。

撤回：打开 validation/glove_direct_bind_20260909/before_direct_glove_bind.blend，或在身体上关闭“穿戴手套_隐藏内部手部”并隐藏左右手套。
'''
text = bpy.data.texts.get('手套直接骨骼绑定说明') or bpy.data.texts.new('手套直接骨骼绑定说明')
text.clear()
text.write(notes)

(ROOT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=OUT_FILE)
print(json.dumps(report, ensure_ascii=False, indent=2))
