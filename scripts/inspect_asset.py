"""Run in background blender to dump scene structure of a reference .blend"""
import bpy, json, sys

out = {
    'objects': [],
    'materials': [],
    'images': [],
    'node_groups': [],
    'worlds': [],
}

for o in bpy.data.objects:
    info = {
        'name': o.name, 'type': o.type,
        'loc': [round(v, 2) for v in o.location],
        'scale': [round(v, 2) for v in o.scale],
        'parent': o.parent.name if o.parent else None,
        'collection': [c.name for c in o.users_collection],
        'modifiers': [{'name': m.name, 'type': m.type,
                       'node_group': (m.node_group.name if m.type == 'NODES' and m.node_group else None)}
                      for m in o.modifiers],
        'materials': [ms.material.name if ms.material else None for ms in o.material_slots],
        'hide_render': o.hide_render,
    }
    if o.type == 'MESH':
        info['verts'] = len(o.data.vertices)
        info['faces'] = len(o.data.polygons)
        info['uv_layers'] = [u.name for u in o.data.uv_layers]
        info['vertex_colors'] = [vc.name for vc in o.data.vertex_colors]
    if o.type == 'EMPTY' and o.instance_collection:
        info['instance_collection'] = o.instance_collection.name
    out['objects'].append(info)

for m in bpy.data.materials:
    mi = {'name': m.name, 'use_nodes': m.use_nodes, 'nodes': []}
    if m.use_nodes:
        for n in m.node_tree.nodes:
            nd = {'name': n.name, 'type': n.bl_idname}
            if n.bl_idname == 'ShaderNodeTexImage' and n.image:
                nd['image'] = n.image.name
                nd['image_path'] = n.image.filepath
            mi['nodes'].append(nd)
    out['materials'].append(mi)

for img in bpy.data.images:
    out['images'].append({'name': img.name, 'path': img.filepath,
                          'size': list(img.size), 'packed': img.packed_file is not None})

for ng in bpy.data.node_groups:
    out['node_groups'].append({
        'name': ng.name,
        'nodes': [(n.name, n.bl_idname) for n in ng.nodes],
    })

for w in bpy.data.worlds:
    out['worlds'].append({'name': w.name,
                          'nodes': [(n.name, n.bl_idname) for n in w.node_tree.nodes] if w.use_nodes else []})

path = r'D:/project/blender_learning/scripts/asset_inspect.json'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('WROTE', path, 'objects:', len(out['objects']))
