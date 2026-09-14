import bpy
import os

scene = bpy.data.scenes["Codex_Cycles_Render"]
bpy.context.window.scene = scene

output = r"D:\project\blender_learning\renders\carthya_pose_cycles_final.png"
blend_copy = r"D:\project\blender_learning\renders\carthya_pose_cycles_setup.blend"
os.makedirs(os.path.dirname(output), exist_ok=True)

scene.render.engine = "CYCLES"
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.015
scene.render.resolution_x = 1350
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = output

bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=blend_copy, copy=True, check_existing=False)
print(output)
print(blend_copy)
