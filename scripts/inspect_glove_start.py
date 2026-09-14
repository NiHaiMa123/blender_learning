import bpy
import json


def info(obj):
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
        'modifiers': [
            {
                'name': m.name,
                'type': m.type,
                'show_viewport': bool(m.show_viewport),
                'show_render': bool(m.show_render),
                'object': getattr(getattr(m, 'object', None), 'name', None),
                'target': getattr(getattr(m, 'target', None), 'name', None),
                'vertex_group': getattr(m, 'vertex_group', None),
                'is_bound': getattr(m, 'is_bound', None),
            }
            for m in obj.modifiers
        ],
        'collections': [c.name for c in obj.users_collection],
    }


names = [
    '达妮娅_mesh', '达妮娅_arm', '左手套', '右手套',
    '左手套.001', '右手套.001', '左手套_腕部装饰', '右手套_腕部装饰',
]
out = {
    'file': bpy.data.filepath,
    'objects': [info(bpy.data.objects[n]) for n in names if n in bpy.data.objects],
    'armatures': [o.name for o in bpy.data.objects if o.type == 'ARMATURE'],
    'hand_glove_objects': [o.name for o in bpy.data.objects if '手套' in o.name],
}
print(json.dumps(out, ensure_ascii=False, indent=2))
