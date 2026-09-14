import bpy
import os

scene = bpy.context.scene
old = (
    scene.render.resolution_x,
    scene.render.resolution_y,
    scene.render.resolution_percentage,
    scene.render.filepath,
)

output = r"D:\project\blender_learning\renders\current_scene_preview.png"
os.makedirs(os.path.dirname(output), exist_ok=True)

scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.filepath = output
bpy.ops.render.render(write_still=False)

save_scene = bpy.data.scenes.new("Codex_Render_Save_Settings")
save_scene.render.image_settings.file_format = "PNG"
bpy.data.images["Render Result"].save_render(filepath=output, scene=save_scene)
bpy.data.scenes.remove(save_scene)

(
    scene.render.resolution_x,
    scene.render.resolution_y,
    scene.render.resolution_percentage,
    scene.render.filepath,
) = old
print(output)
