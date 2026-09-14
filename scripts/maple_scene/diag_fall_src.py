import bpy, json
for gname in ['GN_Falling', 'GN_CarpetScatter', 'GN_Canopy']:
    g = bpy.data.node_groups.get(gname)
    if not g:
        continue
    print('GROUP', gname)
    for n in g.nodes:
        extra = ''
        if n.bl_idname == 'GeometryNodeCollectionInfo' and n.inputs.get('Collection'):
            extra = ' COLL=' + str(n.inputs['Collection'].default_value.name if n.inputs['Collection'].default_value else None)
        if n.bl_idname == 'GeometryNodeObjectInfo' and n.inputs.get('Object'):
            extra = ' OBJ=' + str(n.inputs['Object'].default_value.name if n.inputs['Object'].default_value else None)
        if n.bl_idname == 'GeometryNodeInstanceOnPoints':
            extra = f" pick={n.inputs['Pick Instance'].default_value}"
        print('  ', n.bl_idname, n.name, extra)
