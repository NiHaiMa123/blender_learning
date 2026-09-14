import bpy
fog = bpy.data.objects['FogCube']
print('fog hide_render:', fog.hide_render, 'visible:', fog.visible_get(), 'scale:', tuple(fog.scale))
fm = bpy.data.materials['FogVol']
for l in fm.node_tree.links:
    print('LINK', l.from_node.name, l.from_socket.name, '->', l.to_node.name, l.to_socket.name)
for n in fm.node_tree.nodes:
    print('NODE', n.name, n.bl_idname)
