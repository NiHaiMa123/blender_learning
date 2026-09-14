import bpy
nt = bpy.context.scene.world.node_tree
ramp = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeValToRGB')
mpr = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange')
print('mpr from/to:', mpr.inputs['From Min'].default_value, mpr.inputs['From Max'].default_value,
      mpr.inputs['To Min'].default_value, mpr.inputs['To Max'].default_value)
print('ramp elems:', [(e.position, tuple(e.color)) for e in ramp.color_ramp.elements])
print('links into bg:', [(l.from_node.bl_idname, l.from_socket.name) for l in nt.links if l.to_node.name == '背景'] if any(n.name == '背景' for n in nt.nodes) else 'check names')
for n in nt.nodes:
    print('NODE', n.name, n.bl_idname)
# debug: bottom elem red
ramp.color_ramp.elements[0].color = (1.0, 0.0, 0.0, 1)
s = bpy.context.scene
s.cycles.samples = 8
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 25
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_sky_red.png'
bpy.ops.render.render(write_still=True)
ramp.color_ramp.elements[0].color = (0.7, 0.78, 0.92, 1)
print('DONE')
