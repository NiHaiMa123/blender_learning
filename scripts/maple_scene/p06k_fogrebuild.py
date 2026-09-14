exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

old = bpy.data.objects.get('FogCube')
if old:
    bpy.data.objects.remove(old, do_unlink=True)

# fresh cube, set scale WITHOUT transform_apply (object transform drives world bounds)
bpy.ops.mesh.primitive_cube_add(size=2)
fog = bpy.context.object
fog.name = 'FogCube'
fog.location = (0, 60, 7)
fog.scale = (100, 85, 9)       # x+-100, y -25..145, z -2..16
fog.data.materials.clear()
fog.data.materials.append(bpy.data.materials['FogVol'])
fog.display_type = 'WIRE'
move_to_col(fog, col('BACKGROUND'))

pv = next(n for n in bpy.data.materials['FogVol'].node_tree.nodes
          if n.bl_idname == 'ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.035

save()
bpy.context.scene.cycles.samples = 64
render_preview('p06k_slab_cycles.png', engine='CYCLES', pct=50)
