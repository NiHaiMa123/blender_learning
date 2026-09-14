import bpy, json

obj = bpy.data.objects['卡提希娅_mesh']

source_index = next(
    i for i, slot in enumerate(obj.material_slots)
    if slot.material and slot.material.name == 'Up_Skin'
)
neck_index = next(
    (i for i, slot in enumerate(obj.material_slots)
     if slot.material and slot.material.name == 'Codex_Neck_Skin'),
    None,
)

changed = 0
if neck_index is not None:
    for poly in obj.data.polygons:
        if poly.material_index == neck_index:
            poly.material_index = source_index
            changed += 1

    # The custom neck material was appended as a dedicated final slot.  Once
    # no polygons use it, remove the slot to restore the original assignment.
    obj.data.materials.pop(index=neck_index)

for area in bpy.context.window.screen.areas:
    area.tag_redraw()

path = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)

result = {
    'restored_to': 'Up_Skin',
    'polygons': changed,
    'removed_material_slot': neck_index,
    'saved': path,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
