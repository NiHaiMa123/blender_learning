exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
w = scene.world
nt = w.node_tree

# 1) exposure + sky strength down
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
bg.inputs['Strength'].default_value = 0.5
scene.view_settings.exposure = -0.4

# 2) fog: slightly weaker, greyer
pv = next(n for n in bpy.data.materials['FogVol'].node_tree.nodes
          if n.bl_idname == 'ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.022
pv.inputs['Color'].default_value = (0.5, 0.58, 0.72, 1)

# 3) conifer darker green
cm = bpy.data.materials['ConiferSil']
cb = next(n for n in cm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
cb.inputs['Base Color'].default_value = (0.008, 0.028, 0.022, 1)

# 4) birch greyer
bm = bpy.data.materials['BirchBark']
bb = next(n for n in bm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
bb.inputs['Base Color'].default_value = (0.38, 0.38, 0.36, 1)

# 5) leaf canopy: less translucency -> deeper red under bright sky
lm = bpy.data.materials['MapleLeaf']
mix = next(n for n in lm.node_tree.nodes if n.bl_idname == 'ShaderNodeMixShader')
mix.inputs[0].default_value = 0.28

# 6) grass strip more presence
gs = bpy.data.objects.get('GrassStrip')
gs.location.y = 19
gm = bpy.data.materials['Grass']
gb = next(n for n in gm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
gb.inputs['Base Color'].default_value = (0.09, 0.2, 0.035, 1)

save()
render_preview('p06b_atmo_eevee.png', pct=50)
