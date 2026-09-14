import bpy, json
arm = bpy.data.objects['卡提希娅_arm']
wanted = {'Root', 'センター', 'ＩＫ', '体(上)', '腕', '体(下)', '足', '面'}
result = {}
for collection in arm.data.collections:
    if collection.name in wanted:
        result[collection.name] = [b.name for b in collection.bones]
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
