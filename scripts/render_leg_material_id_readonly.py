import bpy
import colorsys
import json
import os
from mathutils import Vector

scene = bpy.context.scene
character = bpy.data.objects["鸣潮_今汐_桃夭灼灼1.0311_mesh"]
camera = scene.camera
original_materials = [slot.material for slot in character.material_slots]
hidden_meshes = [(obj, obj.hide_render) for obj in scene.objects if obj.type == "MESH" and obj != character]
old_transform = (camera.location.copy(), camera.rotation_mode, camera.rotation_euler.copy(), camera.rotation_quaternion.copy(), camera.data.lens, camera.data.sensor_fit)
old_render = (scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath)

output = r"C:\Users\Administrator\AppData\Local\Temp\opencode\今汐_leg_material_id.png"
os.makedirs(os.path.dirname(output), exist_ok=True)

def aim_at(target):
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = (Vector(target) - camera.location).to_track_quat("-Z", "Y")

mapping = []
id_materials = []
try:
    for obj, _ in hidden_meshes:
        obj.hide_render = True
    camera.location = Vector((0.0, -1.82, 0.72))
    camera.data.lens = 85.0
    camera.data.sensor_fit = "VERTICAL"
    aim_at(Vector((-0.02, 0.02, 0.72)))
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.filepath = output
    for index, slot in enumerate(character.material_slots):
        hue = (index * 0.61803398875) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
        material = bpy.data.materials.new(f"Codex Leg ID {index:02d}")
        material.use_nodes = True
        tree = material.node_tree
        tree.nodes.clear()
        output_node = tree.nodes.new("ShaderNodeOutputMaterial")
        emission = tree.nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = (*rgb, 1.0)
        emission.inputs["Strength"].default_value = 1.0
        tree.links.new(emission.outputs["Emission"], output_node.inputs["Surface"])
        id_materials.append(material)
        mapping.append({"index": index, "material": slot.material.name if slot.material else None, "rgb": [round(value, 3) for value in rgb]})
        slot.material = material
    bpy.ops.render.render(write_still=True)
finally:
    for slot, material in zip(character.material_slots, original_materials):
        slot.material = material
    for obj, hidden in hidden_meshes:
        obj.hide_render = hidden
    camera.location = old_transform[0]
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = old_transform[3]
    camera.rotation_mode = old_transform[1]
    if old_transform[1] != "QUATERNION":
        camera.rotation_euler = old_transform[2]
    camera.data.lens, camera.data.sensor_fit = old_transform[4], old_transform[5]
    scene.render.engine, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old_render

print(json.dumps({"output": output, "mapping": mapping}, ensure_ascii=False, indent=2))
