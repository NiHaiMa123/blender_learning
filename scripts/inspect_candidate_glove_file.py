import bpy
import json


def modifier_info(mod):
    return {
        'name': mod.name,
        'type': mod.type,
        'show_viewport': bool(mod.show_viewport),
        'show_render': bool(mod.show_render),
        'target': getattr(getattr(mod, 'target', None), 'name', None),
        'object': getattr(getattr(mod, 'object', None), 'name', None),
        'vertex_group': getattr(mod, 'vertex_group', None),
        'is_bound': getattr(mod, 'is_bound', None),
    }


def object_info(obj):
    return {
        'name': obj.name,
        'type': obj.type,
        'vertices': len(obj.data.vertices) if obj.type == 'MESH' else None,
        'polygons': len(obj.data.polygons) if obj.type == 'MESH' else None,
        'hide_viewport': bool(obj.hide_viewport),
        'hide_render': bool(obj.hide_render),
        'hide_set': bool(obj.hide_get()),
        'parent': obj.parent.name if obj.parent else None,
        'parent_type': obj.parent_type,
        'parent_bone': obj.parent_bone,
        'modifiers': [modifier_info(m) for m in obj.modifiers],
        'vertex_groups': [g.name for g in obj.vertex_groups] if obj.type == 'MESH' else [],
        'shape_keys': len(obj.data.shape_keys.key_blocks) if obj.type == 'MESH' and obj.data.shape_keys else 0,
        'collections': [c.name for c in obj.users_collection],
    }


interesting = {'达妮娅_mesh', '达妮娅_arm', '左手套', '右手套', '左手套_腕部装饰', '右手套_腕部装饰'}
interesting |= {n for n in bpy.data.objects.keys() if '手套' in n or '手部' in n}
out = {
    'file': bpy.data.filepath,
    'objects': [object_info(bpy.data.objects[n]) for n in sorted(interesting) if n in bpy.data.objects],
    'collections': [
        {
            'name': c.name,
            'hide_viewport': bool(c.hide_viewport),
            'hide_render': bool(c.hide_render),
            'objects': [o.name for o in c.objects if '手套' in o.name or '手部' in o.name],
        }
        for c in bpy.data.collections
        if '手套' in c.name or '手部' in c.name
    ],
}
print(json.dumps(out, ensure_ascii=False, indent=2))
