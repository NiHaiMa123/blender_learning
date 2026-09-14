import bpy,json
from pathlib import Path
root=Path('D:/project/blender_learning/validation/glove_fix_20260909')
view=bpy.app.driver_namespace.get('glove_view_original')
if view:
 for ar in bpy.context.screen.areas:
  if ar.type=='VIEW_3D':
   sp=ar.spaces.active;r=sp.region_3d;r.view_location=view[0];r.view_rotation=view[1];r.view_distance=view[2];sp.overlay.show_overlays=view[3]
body=bpy.data.objects['达妮娅_mesh'];arm=bpy.data.objects['达妮娅_arm']
assert body.modifiers['穿戴手套_隐藏内部手部'].show_viewport
for n in ['右手套','左手套','右手套_腕部装饰','左手套_腕部装饰']:
 o=bpy.data.objects[n];assert not o.hide_viewport and not o.hide_render
 o['穿戴说明']='继续使用达妮娅_arm的原手部骨骼。脱下双手套时，同时关闭身体上的穿戴手套_隐藏内部手部修改器。'
notes=Path('D:/project/blender_learning/GLOVE_FIT_NOTES.md').read_text(encoding='utf8')
text=bpy.data.texts.get('双手套穿戴修复说明') or bpy.data.texts.new('双手套穿戴修复说明');text.clear();text.write(notes)
setup={'mask':'达妮娅_mesh / 穿戴手套_隐藏内部手部','mask_enabled':True,'masked_vertices':6970,'custom_toggle_driver':False,'body_geometry_edited':False,'restored_pose':True,'source_file':'D:/project/blender_learning/达妮娅_鞋子变形修复.blend'}
(root/'wearing_setup.json').write_text(json.dumps(setup,ensure_ascii=False,indent=2),encoding='utf8')
outfile='D:/project/blender_learning/达妮娅_鞋子手套穿戴修复.blend'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=outfile)
for ar in bpy.context.screen.areas:ar.tag_redraw()
print(outfile)
