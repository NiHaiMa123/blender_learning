import bpy
import os

scene = bpy.data.scenes["Codex_Cycles_Render"]
bpy.context.window.scene = scene
scene.cycles.samples = 24
scene.render.resolution_x = 675
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.filepath = r"D:\project\blender_learning\renders\carthya_pose_preview.png"
os.makedirs(os.path.dirname(scene.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)
print(scene.render.filepath)
