import bpy
import json
from mathutils import Matrix


def bone_matrix(armature, name):
    bone = armature.data.bones.get(name)
    pose = armature.pose.bones.get(name)
    return armature.matrix_world @ pose.matrix @ bone.matrix_local.inverted() @ armature.matrix_world.inverted()


def weighted_matrix(obj, vertex, armature):
    matrix = Matrix.Identity(4) * 0.0
    total = 0.0
    terms = []
    for item in vertex.groups:
        group = obj.vertex_groups[item.group]
        if armature.data.bones.get(group.name):
            part = bone_matrix(armature, group.name)
            matrix += item.weight * part
            total += item.weight
            terms.append((group.name, item.weight))
    if total < 1.0:
        matrix += Matrix.Identity(4) * (1.0 - total)
    return matrix, terms


source = bpy.data.objects['达妮娅_红色毛茸袖形态_arm']
target = bpy.data.objects['达妮娅_arm']
obj = bpy.data.objects['右手套']
old_world = obj.matrix_world.copy()
depsgraph = bpy.context.evaluated_depsgraph_get()
source_eval = obj.evaluated_get(depsgraph)
desired = [source_eval.matrix_world @ v.co for v in source_eval.data.vertices]

test = obj.copy()
test.data = obj.data.copy()
test.name = 'DEBUG_DIRECT_TEST'
bpy.context.collection.objects.link(test)
for mod in list(test.modifiers):
    test.modifiers.remove(mod)
test.parent = target
test.matrix_world = old_world
arm_mod = test.modifiers.new('TEST_ARMATURE', 'ARMATURE')
arm_mod.object = target
arm_mod.use_deform_preserve_volume = False
bpy.context.view_layer.update()
ev = test.evaluated_get(bpy.context.evaluated_depsgraph_get())
actual = [ev.matrix_world @ v.co for v in ev.data.vertices]

ids = [0, 100, 500, 1000, 1500, 1900]
out = []
for i in ids:
    if i >= len(obj.data.vertices):
        continue
    dm, terms = weighted_matrix(obj, obj.data.vertices[i], target)
    src_world = old_world @ obj.data.vertices[i].co
    formula = dm @ src_world
    out.append({
        'index': i,
        'terms': terms,
        'src_world': list(src_world),
        'formula_target_on_old': list(formula),
        'actual_target_on_old': list(actual[i]),
        'desired_source': list(desired[i]),
        'formula_actual_error': (formula - actual[i]).length,
        'target_motion': (actual[i] - src_world).length,
    })

bpy.data.objects.remove(test, do_unlink=True)
print(json.dumps(out, ensure_ascii=False, indent=2))
