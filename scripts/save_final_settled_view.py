import bpy
import os

expected = os.path.normcase(r'D:\software\blender\project\今汐_cloth_rebuild_final.blend')
if os.path.normcase(bpy.data.filepath) != expected:
    raise RuntimeError('Refusing to overwrite a non-final Blender file: ' + bpy.data.filepath)

scene = bpy.context.scene
body = bpy.data.objects['CLOTH_REBUILD_BODY_STATIC']
cloth = bpy.data.objects['CLOTH_REBUILD_SKIRT']
collider = bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER']
armature = bpy.data.objects.get('鸣潮_今汐_桃夭灼灼1.0311_arm')

body.hide_viewport = False
body.hide_render = False
cloth.hide_viewport = False
cloth.hide_render = False
collider.hide_viewport = True
collider.hide_render = True
if armature is not None:
    armature.hide_viewport = True
for obj in bpy.context.selected_objects:
    obj.select_set(False)
bpy.context.view_layer.objects.active = None
scene.frame_set(120)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, check_existing=False)
print('FINAL_SETTLED_VIEW|frame=120 body=visible cloth=visible helpers=hidden')
