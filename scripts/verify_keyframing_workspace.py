import bpy, json
window = bpy.context.window
areas = []
for area in window.screen.areas:
    item = {'type': area.type, 'width': area.width, 'height': area.height}
    space = area.spaces.active
    if area.type == 'VIEW_3D':
        item.update({
            'perspective': space.region_3d.view_perspective,
            'shading': space.shading.type,
            'overlays': space.overlay.show_overlays,
        })
    elif area.type == 'DOPESHEET_EDITOR':
        item['mode'] = space.mode
    areas.append(item)
arm = bpy.data.objects['卡提希娅_arm']
result = {
    'workspace': window.workspace.name,
    'screen': window.screen.name,
    'mode': arm.mode,
    'active_object': bpy.context.view_layer.objects.active.name if bpy.context.view_layer.objects.active else None,
    'action': arm.animation_data.action.name if arm.animation_data and arm.animation_data.action else None,
    'auto_key': window.scene.tool_settings.use_keyframe_insert_auto,
    'areas': areas,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
