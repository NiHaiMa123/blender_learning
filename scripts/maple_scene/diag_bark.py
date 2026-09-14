import bpy
m = bpy.data.materials['Bark']
for n in m.node_tree.nodes:
    print(n.bl_idname, '|', n.name, '|', {i.name: (i.default_value if hasattr(i,'default_value') else '') for i in n.inputs if not i.is_linked})
for l in m.node_tree.links:
    print('LINK', l.from_node.name, l.from_socket.name, '->', l.to_node.name, l.to_socket.name)
