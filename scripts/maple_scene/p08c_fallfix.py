exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

em = bpy.data.objects['FallEmitter']
bpy.ops.object.select_all(action='DESELECT')
em.select_set(True)
bpy.context.view_layer.objects.active = em
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

ng = bpy.data.node_groups['GN_Falling']
dist = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsInVolume')
dist.inputs['Density'].default_value = 0.12   # ~345 leaves in 20x24x6m volume

save()
render_preview('p08c_fall_eevee.png', pct=50)
