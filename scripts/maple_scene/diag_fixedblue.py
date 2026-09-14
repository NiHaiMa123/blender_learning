import bpy
nt = bpy.context.scene.world.node_tree
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
for l in list(nt.links):
    if l.to_node == bg:
        nt.links.remove(l)
bg.inputs['Color'].default_value = (0.1, 0.35, 0.9, 1)
s = bpy.context.scene
s.cycles.samples = 8
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 25
s.render.image_settings.file_format = 'PNG'
s.render.film_transparent = False
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_fixedblue.png'
bpy.ops.render.render(write_still=True)
print('DONE')
