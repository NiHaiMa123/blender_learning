exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

nt = bpy.context.scene.world.node_tree
ramp = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeValToRGB')
cr = ramp.color_ramp
# rebuild: pale horizon -> mid blue -> deep zenith
while len(cr.elements) > 1:
    cr.elements.remove(cr.elements[-1])
cr.elements[0].position = 0.0
cr.elements[0].color = (0.72, 0.8, 0.93, 1)
e1 = cr.elements.new(0.5); e1.color = (0.28, 0.48, 0.82, 1)
e2 = cr.elements.new(1.0); e2.color = (0.09, 0.25, 0.68, 1)

save()
bpy.context.scene.cycles.samples = 48
render_preview('p06h_sky_cycles.png', engine='CYCLES', pct=50)
