import bpy
import json

scene = bpy.context.scene
large_meshes = []
for obj in bpy.data.objects:
    if obj.type != 'MESH' or len(obj.data.vertices) < 1000:
        continue
    large_meshes.append({
        'name': obj.name,
        'verts': len(obj.data.vertices),
        'hide_viewport': obj.hide_viewport,
        'hide_render': obj.hide_render,
        'visible_get': obj.visible_get(),
        'parent': obj.parent.name if obj.parent else None,
        'modifiers': [modifier.type for modifier in obj.modifiers],
        'location': [round(float(value), 4) for value in obj.location],
    })

empty = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311')
report = {
    'filepath': bpy.data.filepath,
    'frame': scene.frame_current,
    'empty': {
        'exists': empty is not None,
        'rotation': [round(float(value), 6) for value in empty.rotation_euler] if empty else None,
        'location': [round(float(value), 6) for value in empty.location] if empty else None,
        'hide_viewport': empty.hide_viewport if empty else None,
        'hide_render': empty.hide_render if empty else None,
    },
    'cloth_rebuild_objects': sorted(
        obj.name for obj in bpy.data.objects if obj.name.startswith('CLOTH_REBUILD_')
    ),
    'large_meshes': large_meshes,
}
print('BACKUP_VISIBILITY|' + json.dumps(report, ensure_ascii=False))
