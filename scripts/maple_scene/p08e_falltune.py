exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

ng = bpy.data.node_groups['GN_Falling']
scl = next(n for n in ng.nodes if n.bl_idname == 'FunctionNodeRandomValue'
           and n.data_type == 'FLOAT' and n.inputs['Min'].default_value > 1.0)
scl.inputs['Min'].default_value = 0.8
scl.inputs['Max'].default_value = 1.5

# pull near-camera leaves back: rebuild emitter mesh without y<-6 points
em = bpy.data.objects['FallEmitter']
keep = [tuple(v.co) for v in em.data.vertices if v.co.y >= -6]
print('kept', len(keep), 'of', len(em.data.vertices))
me = bpy.data.meshes.new('FallEmitter_mesh')
me.from_pydata(keep, [], [])
em.data = me

save()
scene = bpy.context.scene
scene.cycles.samples = 128
render_preview('p08e_final_cycles.png', engine='CYCLES', pct=70)
