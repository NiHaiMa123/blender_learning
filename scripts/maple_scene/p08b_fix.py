exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
ng = bpy.data.node_groups['GN_Falling']
floats = [n for n in ng.nodes if n.bl_idname == 'FunctionNodeRandomValue' and n.data_type == 'FLOAT']
for n in floats:
    mx = n.inputs['Max'].default_value
    mn = n.inputs['Min'].default_value
    if abs(mx - 9.6) < 0.5:            # phase node
        n.inputs['Max'].default_value = 6.0
        print('phase -> 6')
    elif abs(mn - 0.8) < 0.05:          # scale node
        n.inputs['Min'].default_value = 1.3
        n.inputs['Max'].default_value = 2.1
        print('scale -> 1.3-2.1')
    elif abs(mn - 1.3) < 0.05:          # speed node (was mangled)
        n.inputs['Min'].default_value = 0.35
        n.inputs['Max'].default_value = 0.9
        print('speed -> 0.35-0.9')
wrap = next(n for n in ng.nodes if n.bl_idname == 'ShaderNodeMath' and n.operation == 'WRAP')
wrap.inputs[2].default_value = 6.0
dist = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsInVolume')
dist.inputs['Density'].default_value = 0.14

# grass band visible
gs = bpy.data.objects['GrassStrip']
gs.location = (0, 20, 0.05)
gs.scale = (90, 7, 1.2)
bpy.ops.object.select_all(action='DESELECT')
gs.select_set(True)
bpy.context.view_layer.objects.active = gs
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
grm = bpy.data.materials['Grass']
gb = next(n for n in grm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
gb.inputs['Base Color'].default_value = (0.05, 0.17, 0.02, 1)

save()
scene.cycles.samples = 128
render_preview('p08_final_cycles.png', engine='CYCLES', pct=70)
