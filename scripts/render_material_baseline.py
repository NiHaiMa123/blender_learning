import bpy
import os

scene = bpy.context.scene
old = (
    scene.render.resolution_x,
    scene.render.resolution_y,
    scene.render.resolution_percentage,
    scene.render.filepath,
)
output = r"D:\project\blender_learning\renders\今汐_before_material_optimization.png"
os.makedirs(os.path.dirname(output), exist_ok=True)
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = output
bpy.ops.render.render(write_still=True)
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old
print(output)
