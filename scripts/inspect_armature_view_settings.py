import bpy, json
arm = bpy.data.objects['卡提希娅_arm']
result = {
    'display_type': arm.data.display_type,
    'show_in_front': arm.show_in_front,
    'show_axes': arm.data.show_axes,
    'relation_line_position': getattr(arm.data, 'relation_line_position', None),
    'views': [],
}
for area in bpy.context.window.screen.areas:
    if area.type != 'VIEW_3D':
        continue
    space = area.spaces.active
    result['views'].append({
        'width': area.width,
        'perspective': space.region_3d.view_perspective,
        'show_overlays': space.overlay.show_overlays,
        'show_bones': getattr(space.overlay, 'show_bones', None),
        'show_outline_selected': getattr(space.overlay, 'show_outline_selected', None),
    })
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
