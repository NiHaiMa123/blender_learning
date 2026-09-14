import bpy
ng = bpy.data.node_groups['GN_Carpet']
# back to ground leaves
coll = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeCollectionInfo'][0]
coll.inputs['Collection'].default_value = bpy.data.collections['LEAF_GROUND_SRC']
inst = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeInstanceOnPoints'][0]
join = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeJoinGeometry'][0]
outp = [n for n in ng.nodes if n.bl_idname == 'NodeGroupOutput'][0]
real = ng.nodes.new('GeometryNodeRealizeInstances')
for l in list(ng.links):
    if l.to_node == join or l.to_node == outp:
        ng.links.remove(l)
ng.links.new(inst.outputs['Instances'], real.inputs['Geometry'])
ng.links.new(real.outputs['Geometry'], join.inputs['Geometry'])
ng.links.new(join.outputs['Geometry'], outp.inputs['Geometry'])

# cut density way down for test
dist = [n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces'][0]
for l in list(ng.links):
    if l.to_node == dist and l.to_socket.name == 'Density':
        ng.links.remove(l)
dist.inputs['Density'].default_value = 15.0

s = bpy.context.scene
s.cycles.samples = 24
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 30
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_realize.png'
bpy.ops.render.render(write_still=True)
print('DONE')
