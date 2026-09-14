import bpy, json, os

scene = bpy.data.scenes['Codex_Cycles_Render']
arm = bpy.data.objects['卡提希娅_arm']

max_basis_delta = 0.0
for pb in arm.pose.bones:
    identity = pb.matrix_basis.copy()
    identity.identity()
    delta = max(abs(a - b) for row_a, row_b in zip(pb.matrix_basis, identity) for a, b in zip(row_a, row_b))
    max_basis_delta = max(max_basis_delta, delta)

visible_render_meshes = [
    o.name for o in scene.objects
    if o.type == 'MESH' and not o.hide_render and not any(c.hide_render for c in o.users_collection if c.name.startswith('Codex_Character_Physics'))
]

old = (scene.render.filepath, scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples)
path = r'D:\project\blender_learning\renders\carthya_character_only_rest_pose_preview.png'
try:
    scene.render.filepath = path
    scene.render.resolution_x = 360
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 20
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.window.scene = scene
    bpy.ops.render.render(write_still=True)
finally:
    scene.render.filepath, scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples = old

result = {
    'scene_children': [c.name for c in scene.collection.children],
    'visible_render_meshes': visible_render_meshes,
    'max_pose_basis_delta': max_basis_delta,
    'preview': path,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
