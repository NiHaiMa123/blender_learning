import bpy, os

scene = bpy.data.scenes['Codex_Cycles_Render']
obj = bpy.data.objects['卡提希娅_mesh']
bpy.context.window.scene = scene

original_materials = [slot.material for slot in obj.material_slots]
old_path = scene.render.filepath
old_x, old_y = scene.render.resolution_x, scene.render.resolution_y
old_samples = scene.cycles.samples

clay = bpy.data.materials.get('Codex_Character_Clay') or bpy.data.materials.new('Codex_Character_Clay')
clay.use_nodes = True
bsdf = clay.node_tree.nodes.get('Principled BSDF') or next(n for n in clay.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf.inputs['Base Color'].default_value = (0.8, 0.82, 0.86, 1.0)
bsdf.inputs['Roughness'].default_value = 0.48

try:
    for slot in obj.material_slots:
        slot.material = clay
    scene.cycles.samples = 24
    scene.render.resolution_x = 675
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.filepath = r'D:\project\blender_learning\renders\carthya_pose_clay_check.png'
    os.makedirs(os.path.dirname(scene.render.filepath), exist_ok=True)
    bpy.ops.render.render(write_still=True)
finally:
    for slot, mat in zip(obj.material_slots, original_materials):
        slot.material = mat
    scene.render.filepath = old_path
    scene.render.resolution_x, scene.render.resolution_y = old_x, old_y
    scene.cycles.samples = old_samples

print(r'D:\project\blender_learning\renders\carthya_pose_clay_check.png')
