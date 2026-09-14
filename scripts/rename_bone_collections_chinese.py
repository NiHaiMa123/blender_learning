import bpy, os, json

arm = bpy.data.objects['卡提希娅_arm']
mapping = {
    'mmd_shadow': '【辅助】影子骨（勿动）',
    'mmd_dummy': '【辅助】虚拟骨（勿动）',
    'Root': '【主控】总控制',
    'センター': '【主控】中心与腰',
    'ＩＫ': '【主控】脚部IK',
    '体(上)': '【身体】上半身与头',
    '腕': '【身体】手臂与手腕',
    '指': '【身体】手指',
    '体(下)': '【身体】骨盆',
    '足': '【身体】腿部',
    '面': '【表情】眼睛',
    '髪': '【物理】头发',
    'リボン': '【物理】飘带与披袖',
    'スカート': '【物理】裙摆',
}

backup = r'D:\project\blender_learning\renders\carthya_before_collection_rename.blend'
output = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
os.makedirs(os.path.dirname(backup), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True, check_existing=False)

renamed = []
for collection in arm.data.collections:
    if collection.name in mapping:
        old = collection.name
        new = mapping[old]
        collection.name = new
        renamed.append({
            'old': old,
            'new': new,
            'visible': collection.is_visible,
            'bones': len(collection.bones),
        })

for area in bpy.context.window.screen.areas:
    area.tag_redraw()

bpy.ops.wm.save_as_mainfile(filepath=output, copy=True, check_existing=False)
result = {'renamed': renamed, 'backup': backup, 'saved': output}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
