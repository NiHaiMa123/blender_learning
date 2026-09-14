import bpy
from pathlib import Path


outfile = Path('D:/project/blender_learning/达妮娅_鞋子变形修复_手套替代手_手臂手指修复_20260909.blend')
body = bpy.data.objects.get('达妮娅_mesh')
arm = bpy.data.objects.get('达妮娅_arm')

if body:
    body['手套替代手_修复说明'] = '只遮罩内部手皮肤与指甲；手臂保留。手套使用素体手部拓扑和逐指骨骼权重。'
if arm:
    arm['手套替代手_修复说明'] = '左右手套直接跟随达妮娅_arm的手腕与各手指骨骼。'

notes = '''手套替代手修复说明

本文件针对手臂消失、手指移动粘连的问题修复。

修复内容：
- 左右手套使用素体手部拓扑与原有逐指骨骼权重，由“达妮娅_arm”直接驱动。
- “达妮娅_mesh”上的“穿戴手套_隐藏内部手部”只遮罩被手套包住的内部手皮肤与指甲，不遮罩手臂。
- 手套保留独立的腕部装饰和材质，不使用会把不同手指错误映射到一起的整手 Surface Deform。

撤回：
- 最安全方式是打开原备份“达妮娅_鞋子变形修复_手套绑定前备份_20260909_193757.blend”。
- 若只想恢复素体手，在“达妮娅_mesh”上关闭“穿戴手套_隐藏内部手部”修改器，并隐藏“左手套”“右手套”及对应腕部装饰。
'''
text = bpy.data.texts.get('手套替代手修复说明') or bpy.data.texts.new('手套替代手修复说明')
text.clear()
text.write(notes)

bpy.ops.wm.save_as_mainfile(filepath=str(outfile))
print(str(outfile))
