import bpy
import json
import math
from mathutils import Quaternion


def evaluated_world_vertices(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    return [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]


def bone_vertex_count(mesh, bone_name, threshold=0.001):
    group = mesh.vertex_groups.get(bone_name)
    if group is None:
        return 0
    index = group.index
    return sum(
        1 for vertex in mesh.data.vertices
        if any(item.group == index and item.weight > threshold for item in vertex.groups)
    )


body = bpy.data.objects['达妮娅_mesh']
arm = bpy.data.objects['达妮娅_arm']
mask = body.modifiers.get('穿戴手套_隐藏内部手部')
group = body.vertex_groups.get('手套穿戴_内部皮肤与指甲')

out = {
    'file': bpy.data.filepath,
    'body_mask': {
        'exists': bool(mask),
        'show_viewport': bool(mask.show_viewport) if mask else None,
        'show_render': bool(mask.show_render) if mask else None,
        'vertex_group': mask.vertex_group if mask else None,
        'masked_vertices': 0,
    },
    'body_bone_weight_counts': {},
    'gloves': {},
}

if group:
    group_index = group.index
    out['body_mask']['masked_vertices'] = sum(
        1 for vertex in body.data.vertices
        if any(item.group == group_index and item.weight > 0.5 for item in vertex.groups)
    )

for name in ['腕.L', '腕.R', 'ひじ.L', 'ひじ.R', '手首.L', '手首.R']:
    out['body_bone_weight_counts'][name] = bone_vertex_count(body, name)

for side, name in [('L', '左手套'), ('R', '右手套')]:
    glove = bpy.data.objects[name]
    finger_groups = [
        f'{finger}{joint}.{side}'
        for finger in ['親指', '人指', '中指', '薬指', '小指']
        for joint in ['０', '１', '２', '３']
    ]
    out['gloves'][name] = {
        'vertices': len(glove.data.vertices),
        'polygons': len(glove.data.polygons),
        'armature_modifier': next(
            (getattr(mod.object, 'name', None) for mod in glove.modifiers if mod.type == 'ARMATURE'),
            None,
        ),
        'finger_weight_groups_present': [g for g in finger_groups if glove.vertex_groups.get(g)],
    }

# Verify independent finger motion without saving the temporary pose.
bpy.context.view_layer.update()
before = {name: evaluated_world_vertices(bpy.data.objects[name]) for name in ['左手套', '右手套']}
original = {}
for bone_name in ['人指１.L', '人指１.R']:
    pose_bone = arm.pose.bones.get(bone_name)
    if pose_bone:
        original[bone_name] = (
            pose_bone.location.copy(),
            pose_bone.rotation_mode,
            pose_bone.rotation_quaternion.copy(),
            pose_bone.rotation_euler.copy(),
            pose_bone.rotation_axis_angle[:],
            pose_bone.scale.copy(),
        )
        pose_bone.rotation_mode = 'QUATERNION'
        pose_bone.rotation_quaternion = pose_bone.rotation_quaternion @ Quaternion((1, 0, 0), math.radians(15))
bpy.context.view_layer.update()
after = {name: evaluated_world_vertices(bpy.data.objects[name]) for name in ['左手套', '右手套']}
for bone_name, values in original.items():
    pose_bone = arm.pose.bones[bone_name]
    pose_bone.location = values[0]
    pose_bone.rotation_mode = values[1]
    pose_bone.rotation_quaternion = values[2]
    pose_bone.rotation_euler = values[3]
    pose_bone.rotation_axis_angle = values[4]
    pose_bone.scale = values[5]
bpy.context.view_layer.update()

for name in ['左手套', '右手套']:
    if before[name] and after[name]:
        out['gloves'][name]['15deg_index_motion'] = max(
            (after[name][i] - before[name][i]).length for i in range(min(len(before[name]), len(after[name])))
        )

print(json.dumps(out, ensure_ascii=False, indent=2))
