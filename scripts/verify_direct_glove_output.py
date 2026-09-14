import bpy
import json
import math
from mathutils import Quaternion


arm = bpy.data.objects['达妮娅_arm']


def verts(name):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj = bpy.data.objects[name]
    evaluated = obj.evaluated_get(depsgraph)
    return [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]


def snapshot(name):
    bone = arm.pose.bones[name]
    return (bone.rotation_mode, bone.rotation_quaternion.copy(), bone.rotation_euler.copy(), bone.rotation_axis_angle[:])


def restore(name, state):
    bone = arm.pose.bones[name]
    bone.rotation_mode = state[0]
    bone.rotation_quaternion = state[1]
    bone.rotation_euler = state[2]
    bone.rotation_axis_angle = state[3]


def test(source_bone, side):
    before = {name: verts(name) for name in ['左手套', '右手套']}
    state = snapshot(source_bone)
    bone = arm.pose.bones[source_bone]
    bone.rotation_mode = 'QUATERNION'
    bone.rotation_quaternion = bone.rotation_quaternion @ Quaternion((1, 0, 0), math.radians(15))
    bpy.context.view_layer.update()
    after = {name: verts(name) for name in ['左手套', '右手套']}
    restore(source_bone, state)
    bpy.context.view_layer.update()
    return {
        'driven_side_max_motion': max((after[side][i] - before[side][i]).length for i in range(len(before[side]))),
        'opposite_side_max_motion': max((after['右手套' if side == '左手套' else '左手套'][i] - before['右手套' if side == '左手套' else '左手套'][i]).length for i in range(len(before[side]))),
    }


out = {
    'file': bpy.data.filepath,
    'left_index_only': test('人指１.L', '左手套'),
    'right_index_only': test('人指１.R', '右手套'),
}
print(json.dumps(out, ensure_ascii=False, indent=2))
