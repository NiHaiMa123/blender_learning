exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

# fog: thinner + huge cube so no faces in frame
pv = next(n for n in bpy.data.materials['FogVol'].node_tree.nodes
          if n.bl_idname == 'ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.009

fog = bpy.data.objects['FogCube']
fog.location = (0, 60, 45)
fog.scale = (500, 400, 120)
bpy.context.view_layer.objects.active = fog
fog.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
fog.select_set(False)

save()
render_preview('p06f_fogfix_eevee.png', pct=50)
bpy.context.scene.cycles.samples = 64
render_preview('p06f_fogfix_cycles.png', engine='CYCLES', pct=50)
