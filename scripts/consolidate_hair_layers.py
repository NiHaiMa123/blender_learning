import bpy

obj = bpy.data.objects['卡提希娅_mesh']
base_bangs = bpy.data.materials.get('Hair_Bangs')
base_back = bpy.data.materials.get('Hair_Back')
if not base_bangs or not base_back:
    raise RuntimeError('Base hair materials missing')

changed = []
for index, slot in enumerate(obj.material_slots):
    if slot.material and slot.material.name == 'Hair_Bangs+':
        slot.material = base_bangs
        changed.append((index, 'Hair_Bangs+', 'Hair_Bangs'))
    elif slot.material and slot.material.name == 'Hair_Back+':
        slot.material = base_back
        changed.append((index, 'Hair_Back+', 'Hair_Back'))

print(str(changed))
return_value = changed
