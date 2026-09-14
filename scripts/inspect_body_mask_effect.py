import bpy
import json


body = bpy.data.objects['达妮娅_mesh']
mask = body.modifiers.get('穿戴手套_隐藏内部手部')
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = body.evaluated_get(depsgraph)
out = {
    'file': bpy.data.filepath,
    'mask': {
        'exists': bool(mask),
        'vertex_group': mask.vertex_group if mask else None,
        'invert': bool(mask.invert_vertex_group) if mask else None,
        'show_viewport': bool(mask.show_viewport) if mask else None,
    },
    'base_vertices': len(body.data.vertices),
    'evaluated_vertices': len(evaluated.data.vertices),
    'base_polygons': len(body.data.polygons),
    'evaluated_polygons': len(evaluated.data.polygons),
}
print(json.dumps(out, ensure_ascii=False, indent=2))
