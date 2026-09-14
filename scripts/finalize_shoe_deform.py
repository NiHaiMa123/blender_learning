import bpy,json,numpy as np
from pathlib import Path
root=Path('D:/project/blender_learning/validation/shoe_fix_20260909')
arm=bpy.data.objects['达妮娅_arm']
saved=bpy.app.driver_namespace.pop('shoe_visual_test_original',None)
if saved:
    for n,q in saved.items():arm.pose.bones[n].rotation_quaternion=q
bpy.context.view_layer.update()
report={}
for n in ['达妮娅_mesh','左鞋子_鞋面','右鞋子_鞋面','左鞋子_脚部','右鞋子_脚部']:
    o=bpy.data.objects[n];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    current=np.array([e.matrix_world@v.co for v in e.data.vertices])
    error=float(np.max(np.linalg.norm(current-np.load(root/(n+'_before.npy')),axis=1)))
    assert error<1e-6,(n,error)
    report[n]=error
for n in ['左鞋子_鞋面','右鞋子_鞋面','左鞋子_脚部','右鞋子_脚部']:
    o=bpy.data.objects[n];m=o.modifiers.get('鞋子随脚变形_保持当前贴合')
    assert m and m.is_bound
text=bpy.data.texts.new('鞋子变形修复说明')
text.write('修复日期：2026-09-09\n四个鞋部件从单一脚踝骨骼父级跟随改为表面变形。\n当前已调好的姿势作为绑定基准，身体未改动，鞋子顶点变化低于 0.000001 Blender 单位。\n继续操作原来的 足首D.L / 足首D.R 和 足先EX.L / 足先EX.R 即可。\n鞋子变形_辅助 集合内两个隐藏网格负责跟随身体脚部骨骼，请保留它们及鞋子的表面变形修改器。\n这是绑定式变形，不是实时碰撞模拟。测试覆盖脚踝 X ±25°，Y/Z ±15°，脚趾 X ±15°。\n保持原位置也保留了原有微小交叠；右踝侧转 +15° 测试中鞋帮三角面交叠对数由 19 到 21，极端姿势可能仍需修形。\n原场景备份：validation/shoe_fix_20260909/before_shoe_deform.blend\n')
outfile='D:/project/blender_learning/达妮娅_鞋子变形修复.blend'
bpy.ops.wm.save_as_mainfile(filepath=outfile)
report['saved_file']=outfile;report['blender_binary']=bpy.app.binary_path
(root/'final_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for a in bpy.context.screen.areas:a.tag_redraw()
print(json.dumps(report,ensure_ascii=False))
