import bpy
nt = bpy.context.scene.world.node_tree
for l in nt.links:
    print('LINK', l.from_node.name, '->', l.to_node.name, '|', l.from_socket.name, '->', l.to_socket.name)
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
for i in bg.inputs:
    print('bg input', i.name, 'linked' if i.links else 'unlinked', getattr(i, 'default_value', None))
