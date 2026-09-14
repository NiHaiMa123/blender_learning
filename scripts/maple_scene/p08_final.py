exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene

# ---------- falling leaves: bigger, denser near top ----------
em = bpy.data.objects['FallEmitter']
# shrink volume to upper air so wrapped leaves stay in frame
em.location = (1, 2, 7.0)
em.scale = (10, 12, 3.0)
ng = bpy.data.node_groups['GN_Falling']
scl = next(n for n in ng.nodes if n.bl_idname == 'FunctionNodeRandomValue' and n.data_type == 'FLOAT')
scl.inputs['Min'].default_value = 1.3
scl.inputs['Max'].default_value = 2.1
dist = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsInVolume')
dist.inputs['Density'].default_value = 0.14
# fall range shorter: H=6 -> leaves spread z 1..10
wrap = next(n for n in ng.nodes if n.bl_idname == 'ShaderNodeMath' and n.operation == 'WRAP')
wrap.inputs[2].default_value = 6.0
phase = next(n for n in ng.nodes if n.bl_idname == 'FunctionNodeRandomValue' and n.data_type == 'FLOAT' and n.inputs['Max'].default_value == 9.6)
phase.inputs['Max'].default_value = 6.0

# ---------- grass band: closer + greener mound between carpet and forest ----------
gs = bpy.data.objects['GrassStrip']
gs.location = (0, 20, 0.05)
gs.scale = (90, 7, 1.2)
bpy.context.view_layer.objects.active = gs
gs.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
gs.select_set(False)
grm = bpy.data.materials['Grass']
gb = next(n for n in grm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
gb.inputs['Base Color'].default_value = (0.05, 0.17, 0.02, 1)

# ---------- final cycles render ----------
save()
scene.cycles.samples = 128
scene.render.resolution_percentage = 70
render_preview('p08_final_cycles.png', engine='CYCLES', pct=70)
