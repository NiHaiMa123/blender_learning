import bpy
em = bpy.data.objects.get('FallEmitter')
print('emitter loc/scale:', tuple(em.location), tuple(em.scale))
gs = bpy.data.objects.get('GrassStrip')
print('grass loc/scale:', tuple(gs.location), tuple(gs.scale))
ng = bpy.data.node_groups['GN_Falling']
for n in ng.nodes:
    if n.bl_idname == 'FunctionNodeRandomValue' and n.data_type == 'FLOAT':
        print('float rand:', n.inputs['Min'].default_value, n.inputs['Max'].default_value)
import os
print('blend saved?', os.path.exists(r'D:/project/blender_learning/maple_scene.blend'))
