import bpy
g = bpy.data.objects['Ground']
mod = g.modifiers['carpet']
mod.show_render = False
s = bpy.context.scene
s.cycles.samples = 16
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 30
s.render.image_settings.file_format = 'PNG'
s.render.filepath = r'D:/project/blender_learning/renders/maple/diag_no_carpet.png'
bpy.ops.render.render(write_still=True)
mod.show_render = True

# also inspect gleaf materials
for o in bpy.data.collections['LEAF_GROUND_SRC'].objects:
    print('GLEAF', o.name, [ms.material.name if ms.material else None for ms in o.material_slots],
          set(p.material_index for p in o.data.polygons), 'mods', [m.type for m in o.modifiers])
print('DONE')
