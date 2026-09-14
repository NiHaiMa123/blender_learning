import bpy, json

arm = bpy.data.objects['卡提希娅_arm']
arm.data.display_type = 'STICK'
arm.show_in_front = True

views = []
for area in bpy.context.window.screen.areas:
    if area.type != 'VIEW_3D':
        continue
    space = area.spaces.active
    is_camera = space.region_3d.view_perspective == 'CAMERA'
    space.overlay.show_bones = not is_camera
    space.overlay.show_overlays = not is_camera
    if hasattr(space.overlay, 'show_text'):
        space.overlay.show_text = not is_camera
    if hasattr(space.overlay, 'show_outline_selected'):
        space.overlay.show_outline_selected = not is_camera
    views.append({
        'width': area.width,
        'camera': is_camera,
        'show_bones': space.overlay.show_bones,
        'show_overlays': space.overlay.show_overlays,
    })

path = r'D:\project\blender_learning\renders\carthya_keyframing_workspace.blend'
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)
result = {'display_type': arm.data.display_type, 'views': views, 'saved': path}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
