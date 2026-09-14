exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
nt = scene.world.node_tree
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.09, 0.3, 0.82, 1)
bg.inputs['Strength'].default_value = 0.7
# drop the dead gradient nodes
for n in list(nt.nodes):
    if n.bl_idname in ('ShaderNodeTexCoord', 'ShaderNodeSeparateXYZ',
                       'ShaderNodeMapRange', 'ShaderNodeValToRGB'):
        nt.nodes.remove(n)

# fog back on (height gradient already inside material)
fog = bpy.data.objects['FogCube']
fog.hide_render = False

save()
scene.cycles.samples = 64
render_preview('p06i_final_cycles.png', engine='CYCLES', pct=50)
