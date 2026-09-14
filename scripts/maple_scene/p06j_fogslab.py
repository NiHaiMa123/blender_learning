exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene

# fog slab: constant density, low-altitude band only
fm = bpy.data.materials['FogVol']
nt = fm.node_tree
pv = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeVolumePrincipled')
for l in list(nt.links):
    if l.to_socket == pv.inputs['Density']:
        nt.links.remove(l)
for n in list(nt.nodes):
    if n.bl_idname in ('ShaderNodeNewGeometry', 'ShaderNodeSeparateXYZ',
                       'ShaderNodeMapRange', 'ShaderNodeMath'):
        nt.nodes.remove(n)
pv.inputs['Density'].default_value = 0.03
pv.inputs['Color'].default_value = (0.58, 0.66, 0.8, 1)
pv.inputs['Anisotropy'].default_value = 0.3

fog = bpy.data.objects['FogCube']
fog.location = (0, 60, 7)
fog.scale = (200, 170, 9)      # z band -2 .. 16
bpy.context.view_layer.objects.active = fog
fog.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
fog.select_set(False)

# remove mini test cube
mini = bpy.data.objects.get('MiniFog')
if mini:
    bpy.data.objects.remove(mini, do_unlink=True)

# camera sees further (mountains at y~95 were clipped at 100m)
cam = bpy.data.objects.get('Camera')
cam.data.clip_end = 600.0

save()
scene.cycles.samples = 64
render_preview('p06j_slab_cycles.png', engine='CYCLES', pct=50)
