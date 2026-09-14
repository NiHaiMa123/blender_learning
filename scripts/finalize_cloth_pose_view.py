import bpy
import json

scene = bpy.context.scene
body = bpy.data.objects['CLOTH_REBUILD_BODY_STATIC']
cloth = bpy.data.objects['CLOTH_REBUILD_SKIRT']
collider = bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER']
armature = bpy.data.objects['鸣潮_今汐_桃夭灼灼1.0311_arm']
source = bpy.data.objects['鸣潮_今汐_桃夭灼灼1.0311_mesh']
root = bpy.data.objects['鸣潮_今汐_桃夭灼灼1.0311']

body.hide_viewport = False
body.hide_render = False
cloth.hide_viewport = False
cloth.hide_render = False
collider.hide_viewport = True
collider.hide_render = True
armature.hide_viewport = True
source.hide_viewport = True
source.hide_render = True
for selected in bpy.context.selected_objects:
    selected.select_set(False)
bpy.context.view_layer.objects.active = None
scene.frame_set(80)
bpy.ops.wm.save_mainfile()

report = {
    'filepath': bpy.data.filepath,
    'frame': scene.frame_current,
    'body_visible': body.visible_get(),
    'cloth_visible': cloth.visible_get(),
    'collider_hidden': collider.hide_viewport,
    'armature_hidden': armature.hide_viewport,
    'root_location': [round(float(value), 6) for value in root.location],
    'root_rotation': [round(float(value), 6) for value in root.rotation_euler],
}
print('FINALIZE_POSE_VIEW|' + json.dumps(report, ensure_ascii=False))
