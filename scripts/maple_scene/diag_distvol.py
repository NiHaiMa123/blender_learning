import bpy
em = bpy.data.objects['FallEmitter']
print('mods:', [(m.name, m.type) for m in em.modifiers])
ng = bpy.data.node_groups['GN_Falling']
dist = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsInVolume')
for i in dist.inputs:
    print('IN', i.name, i.type, getattr(i, 'default_value', '-'), 'linked' if i.links else '')
for o in dist.outputs:
    print('OUT', o.name, o.type)
