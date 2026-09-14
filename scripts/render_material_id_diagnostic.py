import bpy, colorsys, json, os

scene = bpy.data.scenes['Codex_Cycles_Render']
obj = bpy.data.objects['卡提希娅_mesh']
bpy.context.window.scene = scene
original_materials = [slot.material for slot in obj.material_slots]
old_path = scene.render.filepath
old_x, old_y = scene.render.resolution_x, scene.render.resolution_y
old_samples = scene.cycles.samples
mapping = []

try:
    for i, slot in enumerate(obj.material_slots):
        # Golden-ratio hue spacing makes adjacent material indices distinct.
        h = (i * 0.61803398875) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.80, 1.0)
        mat = bpy.data.materials.get(f'Codex_ID_{i:02d}') or bpy.data.materials.new(f'Codex_ID_{i:02d}')
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = (r, g, b, 1.0)
        em.inputs['Strength'].default_value = 1.0
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
        name = original_materials[i].name if original_materials[i] else '<None>'
        mapping.append({"index": i, "name": name, "rgb": [round(r, 3), round(g, 3), round(b, 3)]})
        slot.material = mat

    scene.cycles.samples = 8
    scene.render.resolution_x = 675
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.filepath = r'D:\project\blender_learning\renders\carthya_material_id_check.png'
    os.makedirs(os.path.dirname(scene.render.filepath), exist_ok=True)
    bpy.ops.render.render(write_still=True)
finally:
    for slot, mat in zip(obj.material_slots, original_materials):
        slot.material = mat
    scene.render.filepath = old_path
    scene.render.resolution_x, scene.render.resolution_y = old_x, old_y
    scene.cycles.samples = old_samples

print(json.dumps(mapping, ensure_ascii=False))
return_value = mapping
