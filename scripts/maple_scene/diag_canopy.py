import bpy, json
out = []
for o in bpy.data.objects:
    gn = [(m.name, m.node_group.name if m.node_group else None) for m in o.modifiers if m.type == 'NODES']
    if gn or 'Emitter' in o.name or 'leaf' in o.name.lower():
        out.append({'name': o.name, 'type': o.type, 'gn': gn, 'hide': o.hide_render,
                    'verts': len(o.data.vertices) if o.type == 'MESH' else 0,
                    'coll': [c.name for c in o.users_collection]})
print('CANOPYINFO ' + json.dumps(out, ensure_ascii=False))
