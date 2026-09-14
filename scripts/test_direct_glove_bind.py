import bpy
import json
from mathutils import Matrix


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


def vertex_deform_matrix(obj, vertex, armature):
    matrix = Matrix.Identity(4) * 0.0
    total = 0.0
    for item in vertex.groups:
        group_name = obj.vertex_groups[item.group].name
        bone_matrix = deform_matrix(armature, group_name)
        if bone_matrix is not None:
            matrix += item.weight * bone_matrix
            total += item.weight
    if total > 1.0:
        return matrix * (1.0 / total)
    return matrix + Matrix.Identity(4) * (1.0 - total)


def make_test_object(original, source, target):
    old_world = original.matrix_world.copy()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    original_eval = original.evaluated_get(depsgraph)
    desired = [original_eval.matrix_world @ v.co for v in original_eval.data.vertices]

    out = original.copy()
    out.data = original.data.copy()
    out.name = original.name + '_DIRECT_TEST'
    bpy.context.collection.objects.link(out)
    for mod in list(out.modifiers):
        out.modifiers.remove(mod)
    out.parent = target
    out.matrix_world = old_world

    # Calibrate every shape-key block in the current target pose. This keeps
    # the current fit while retaining all original morphs.
    for vertex_index, vertex in enumerate(original.data.vertices):
        target_deform = vertex_deform_matrix(original, vertex, target)
        inverse_target = target_deform.inverted_safe()
        for key in out.data.shape_keys.key_blocks if out.data.shape_keys else []:
            source_co = original.data.shape_keys.key_blocks[key.name].data[vertex_index].co
            source_world = old_world @ source_co
            target_rest_world = inverse_target @ source_world
            key.data[vertex_index].co = old_world.inverted() @ target_rest_world

    if out.data.shape_keys is None:
        for vertex_index, vertex in enumerate(original.data.vertices):
            target_deform = vertex_deform_matrix(original, vertex, target)
            source_world = desired[vertex_index]
            target_rest_world = target_deform.inverted_safe() @ source_world
            vertex.co = old_world.inverted() @ target_rest_world

    modifier = out.modifiers.new('DIRECT_TEST_ARMATURE', 'ARMATURE')
    modifier.object = target
    modifier.use_deform_preserve_volume = False
    bpy.context.view_layer.update()
    evaluated = out.evaluated_get(bpy.context.evaluated_depsgraph_get())
    actual = [evaluated.matrix_world @ v.co for v in evaluated.data.vertices]
    error = max((actual[i] - desired[i]).length for i in range(len(desired)))
    bpy.data.objects.remove(out, do_unlink=True)
    return error


source = bpy.data.objects['达妮娅_红色毛茸袖形态_arm']
target = bpy.data.objects['达妮娅_arm']
report = {}
for name in ['左手套', '右手套']:
    report[name] = make_test_object(bpy.data.objects[name], source, target)
print(json.dumps(report, ensure_ascii=False, indent=2))
