import bpy, json

window = bpy.context.window
scene = window.scene
arm = bpy.data.objects['卡提希娅_arm']

for obj in bpy.context.view_layer.objects:
    obj.select_set(False)
arm.hide_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

# Force Blender to rebuild the pose draw cache rather than retaining the
# previous octahedral batches after a workspace switch.
if arm.mode == 'POSE':
    bpy.ops.object.mode_set(mode='OBJECT')
arm.data.display_type = 'WIRE'
arm.data.update_tag()
bpy.context.view_layer.update()
arm.data.display_type = 'STICK'
arm.data.update_tag()
bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='POSE')
scene.frame_set(scene.frame_current)

views = []
for area in window.screen.areas:
    if area.type == 'VIEW_3D':
        space = area.spaces.active
        is_camera = space.region_3d.view_perspective == 'CAMERA'
        space.overlay.show_bones = not is_camera
        space.overlay.show_overlays = not is_camera
        area.tag_redraw()
        views.append({'camera': is_camera, 'show_bones': space.overlay.show_bones})

for area in window.screen.areas:
    area.tag_redraw()

try:
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
except Exception:
    pass

result = {'display_type': arm.data.display_type, 'mode': arm.mode, 'views': views}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
