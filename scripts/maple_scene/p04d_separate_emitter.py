exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

ground = bpy.data.objects['Ground']
gcol = col('GROUND')

# remove broken carpet GN from Ground
old = ground.modifiers.get('carpet')
if old:
    ground.modifiers.remove(old)

# ---------- fresh scatter node group: input -> dist -> instance -> output ----------
ng = bpy.data.node_groups.get('GN_CarpetScatter')
if ng:
    bpy.data.node_groups.remove(ng)
ng = bpy.data.node_groups.new('GN_CarpetScatter', 'GeometryNodeTree')
ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
inp = ng.nodes.new('NodeGroupInput')
outp = ng.nodes.new('NodeGroupOutput')
dist = ng.nodes.new('GeometryNodeDistributePointsOnFaces')
dist.inputs['Density'].default_value = 120.0
coll = ng.nodes.new('GeometryNodeCollectionInfo')
coll.inputs['Collection'].default_value = bpy.data.collections['LEAF_GROUND_SRC']
coll.inputs['Separate Children'].default_value = True
coll.inputs['Reset Children'].default_value = True
inst = ng.nodes.new('GeometryNodeInstanceOnPoints')
inst.inputs['Pick Instance'].default_value = True
rot = ng.nodes.new('FunctionNodeRandomValue')
rot.data_type = 'FLOAT_VECTOR'
rot.inputs['Min'].default_value = (-0.55, -0.55, -math.pi)
rot.inputs['Max'].default_value = (0.55, 0.55, math.pi)
scl = ng.nodes.new('FunctionNodeRandomValue')
scl.data_type = 'FLOAT'
scl.inputs['Min'].default_value = 0.8
scl.inputs['Max'].default_value = 1.5
ng.links.new(inp.outputs['Geometry'], dist.inputs['Mesh'])
ng.links.new(dist.outputs['Points'], inst.inputs['Points'])
ng.links.new(coll.outputs['Instances'], inst.inputs['Instance'])
ng.links.new(rot.outputs['Value'], inst.inputs['Rotation'])
ng.links.new(scl.outputs['Value'], inst.inputs['Scale'])
ng.links.new(inst.outputs['Instances'], outp.inputs['Geometry'])

# ---------- CarpetEmitter: ground copy, scatter only ----------
old_em = bpy.data.objects.get('CarpetEmitter')
if old_em:
    bpy.data.objects.remove(old_em, do_unlink=True)
em = ground.copy()
em.data = ground.data.copy()
em.name = 'CarpetEmitter'
gcol.objects.link(em)
for m in list(em.modifiers):
    em.modifiers.remove(m)
# keep same undulation as ground
tex = bpy.data.textures['ground_und']
disp = em.modifiers.new('undulate', 'DISPLACE')
disp.texture = tex
disp.strength = 0.22
disp.texture_coords = 'GLOBAL'
mod = em.modifiers.new('carpet', 'NODES')
mod.node_group = ng
em.display_type = 'WIRE'

save()
render_preview('p04d_carpet_eevee.png', pct=50)
