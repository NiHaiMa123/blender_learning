exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
scene.view_settings.exposure = 0.0
nt = scene.world.node_tree
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
bg.inputs['Strength'].default_value = 0.9
ramp = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeValToRGB')
cr = ramp.color_ramp
cr.elements[0].color = (0.7, 0.78, 0.92, 1)
cr.elements[1].color = (0.10, 0.28, 0.72, 1)

save()
# quick eevee check then cycles
render_preview('p06e_bright_eevee.png', pct=50)
scene.cycles.samples = 64
render_preview('p06e_bright_cycles.png', engine='CYCLES', pct=50)
