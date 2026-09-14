exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

# 1) disconnect world volume (blackens eevee)
w = bpy.context.scene.world
nt = w.node_tree
for l in list(nt.links):
    if l.to_socket.name == 'Volume':
        nt.links.remove(l)
for n in list(nt.nodes):
    if n.bl_idname == 'ShaderNodeVolumePrincipled':
        nt.nodes.remove(n)

# 2) fog cube covering the scene -> works in eevee + cycles
old = bpy.data.objects.get('FogCube')
if old:
    bpy.data.objects.remove(old, do_unlink=True)
fm = bpy.data.materials.get('FogVol') or bpy.data.materials.new('FogVol')
fm.use_nodes = True
fm.node_tree.nodes.clear()
fout = fm.node_tree.nodes.new('ShaderNodeOutputMaterial')
pv = fm.node_tree.nodes.new('ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.014
pv.inputs['Color'].default_value = (0.62, 0.72, 0.88, 1)
pv.inputs['Anisotropy'].default_value = 0.2
fm.node_tree.links.new(pv.outputs['Volume'], fout.inputs['Volume'])

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 45, 20))
fog = bpy.context.object
fog.name = 'FogCube'
fog.scale = (110, 90, 30)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
fog.data.materials.append(fm)
fog.display_type = 'WIRE'
move_to_col(fog, col('BACKGROUND'))

save()
render_preview('p05b_fog_eevee.png', pct=50)
