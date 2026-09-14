import bpy
em = bpy.data.objects['FallEmitter']
ng = bpy.data.node_groups['GN_Falling']
outp = next(n for n in ng.nodes if n.bl_idname == 'NodeGroupOutput')
dist = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsInVolume')
# bypass everything: raw points straight to output
for l in list(ng.links):
    if l.to_node == outp:
        ng.links.remove(l)
ng.links.new(dist.outputs['Points'], outp.inputs['Geometry'])
s = bpy.context.scene
s.render.engine = 'BLENDER_WORKBENCH'   # shows point clouds as dots
s.render.resolution_percentage = 50
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_fall_pts.png'
bpy.ops.render.render(write_still=True)
print('DONE')
