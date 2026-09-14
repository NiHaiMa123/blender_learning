import bpy
import colorsys
import json
import os
from mathutils import Vector

scene = bpy.context.scene
character = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
camera = scene.camera
if character is None or camera is None:
    raise RuntimeError("Character or camera not found")

target = Vector((0.02, 0.18, 1.16))
old_camera = (
    camera.location.copy(),
    camera.rotation_mode,
    camera.rotation_euler.copy(),
    camera.rotation_quaternion.copy(),
    camera.data.lens,
)
old_render = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath)
original_materials = [slot.material for slot in character.material_slots]
hidden_meshes = [(obj, obj.hide_render) for obj in scene.objects if obj.type == "MESH" and obj != character]

audit_dir = r"C:\Users\Administrator\AppData\Local\Temp\opencode"
os.makedirs(audit_dir, exist_ok=True)
output = os.path.join(audit_dir, "今汐_material_id_audit.png")

def aim_at(obj, point):
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (Vector(point) - obj.location).to_track_quat("-Z", "Y")

mapping = []
try:
    for obj, _ in hidden_meshes:
        obj.hide_render = True
    camera.location = Vector((0.04, -2.15, 1.16))
    camera.data.lens = 68.0
    aim_at(camera, target)
    scene.render.resolution_x = 960
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output

    id_materials = []
    for index, slot in enumerate(character.material_slots):
        hue = (index * 0.61803398875) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 0.82, 1.0)
        material = bpy.data.materials.new(f"Codex_Audit_ID_{index:02d}")
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

    scene.render.engine = "BLENDER_EEVEE"
    bpy.ops.render.render(write_still=True)
finally:
    for slot, material in zip(character.material_slots, original_materials):
        slot.material = material
    for obj, hidden in hidden_meshes:
        obj.hide_render = hidden
    camera.location = old_camera[0]
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = old_camera[3]
    camera.rotation_mode = old_camera[1]
    if old_camera[1] != "QUATERNION":
        camera.rotation_euler = old_camera[2]
    camera.data.lens = old_camera[4]
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old_render

print(json.dumps({"output": output, "mapping": mapping}, ensure_ascii=False, indent=2))
