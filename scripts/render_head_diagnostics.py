import bpy, colorsys, json, os
from mathutils import Vector

scene = bpy.data.scenes['Codex_Cycles_Render']
obj = bpy.data.objects['卡提希娅_mesh']
arm = bpy.data.objects['卡提希娅_arm']
cam = scene.camera
bpy.context.window.scene = scene

head_bone = None
for name in ('頭', '头', 'Head', 'head'):
    if name in arm.pose.bones:
        head_bone = arm.pose.bones[name]
        break
if head_bone is None:
    candidates = [b for b in arm.pose.bones if ('頭' in b.name or 'head' in b.name.lower())]
    if not candidates:
        raise RuntimeError('Head bone not found')
    head_bone = candidates[0]

target = arm.matrix_world @ ((head_bone.head + head_bone.tail) * 0.5)
target.z -= 0.06

old_cam = (cam.location.copy(), cam.rotation_euler.copy(), cam.data.lens, cam.data.shift_x, cam.data.shift_y)
old_render = (scene.render.filepath, scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples)
original_materials = [slot.material for slot in obj.material_slots]

def render_to(path, samples):
    scene.render.filepath = path
    scene.render.resolution_x = 600
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.cycles.samples = samples
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.render.render(write_still=True)

try:
    cam.location = target + Vector((0.45, -1.55, 0.10))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 92
    cam.data.shift_x = 0
    cam.data.shift_y = 0
    render_to(r'D:\project\blender_learning\renders\carthya_head_color_check.png', 32)

    mapping = []
    for i, slot in enumerate(obj.material_slots):
        h = (i * 0.61803398875) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.80, 1.0)
        mat = bpy.data.materials.get(f'Codex_ID_{i:02d}') or bpy.data.materials.new(f'Codex_ID_{i:02d}')
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        em = nt.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = (r, g, b, 1.0)
        nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
        mapping.append({"index": i, "name": original_materials[i].name if original_materials[i] else '<None>', "rgb": [round(r, 3), round(g, 3), round(b, 3)]})
        slot.material = mat
    render_to(r'D:\project\blender_learning\renders\carthya_head_id_check.png', 8)
finally:
    for slot, mat in zip(obj.material_slots, original_materials):
        slot.material = mat
    cam.location, cam.rotation_euler, cam.data.lens, cam.data.shift_x, cam.data.shift_y = old_cam
    scene.render.filepath, scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples = old_render

print(json.dumps({"head_bone": head_bone.name, "target": list(target)}, ensure_ascii=False))
