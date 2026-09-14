import bpy
fm = bpy.data.materials['FogVol']
pv = next(n for n in fm.node_tree.nodes if n.bl_idname == 'ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.5
mini = bpy.data.objects.get('MiniFog')
if not mini:
    bpy.ops.mesh.primitive_cube_add(size=4, location=(0.5, -10, 1.5))
    mini = bpy.context.object
    mini.name = 'MiniFog'
    mini.data.materials.append(fm)
s = bpy.context.scene
s.cycles.samples = 16
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 30
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_minifog2.png'
bpy.ops.render.render(write_still=True)
pv.inputs['Density'].default_value = 0.02
print('DONE')
