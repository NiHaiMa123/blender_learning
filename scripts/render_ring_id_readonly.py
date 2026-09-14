import bpy
import os
from mathutils import Vector

scene = bpy.context.scene
camera = scene.camera
obj = bpy.data.objects["鸣潮_今汐_桃夭灼灼1.0311_mesh"]
ring_slot = next(index for index, slot in enumerate(obj.material_slots) if slot.material and slot.material.name == "metal leg")
original = obj.material_slots[ring_slot].material
old_transform = (camera.location.copy(), camera.rotation_mode, camera.rotation_euler.copy(), camera.rotation_quaternion.copy(), camera.data.lens, camera.data.sensor_fit)
old_render = (scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath)

material = bpy.data.materials.get("Codex Ring ID Readonly") or bpy.data.materials.new("Codex Ring ID Readonly")
material.use_nodes = True
tree = material.node_tree
tree.nodes.clear()
output = tree.nodes.new("ShaderNodeOutputMaterial")

target = Vector((-0.02, 0.02, 0.72))
try:
    obj.material_slots[ring_slot].material = material
    camera.location = Vector((0.0, -1.82, 0.72))
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = (target - camera.location).to_track_quat("-Z", "Y")
    camera.data.lens = 85.0
    camera.data.sensor_fit = "VERTICAL"
    output_path = r"C:\Users\Administrator\AppData\Local\Temp\opencode\今汐_ring_id_readonly.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
finally:
    obj.material_slots[ring_slot].material = original
    camera.location = old_transform[0]
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = old_transform[3]
    camera.rotation_mode = old_transform[1]
    if old_transform[1] != "QUATERNION":
        camera.rotation_euler = old_transform[2]
    camera.data.lens, camera.data.sensor_fit = old_transform[4], old_transform[5]
    scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old_render

print(output_path)
