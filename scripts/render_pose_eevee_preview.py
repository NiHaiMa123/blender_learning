import bpy
import os

scene = bpy.data.scenes["Codex_Cycles_Render"]
bpy.context.window.scene = scene
old_engine = scene.render.engine
old_x, old_y = scene.render.resolution_x, scene.render.resolution_y
old_path = scene.render.filepath

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 675
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.filepath = r"D:\project\blender_learning\renders\carthya_pose_eevee_check.png"
os.makedirs(os.path.dirname(scene.render.filepath), exist_ok=True)
bpy.ops.render.render(write_still=True)

scene.render.engine = old_engine
scene.render.resolution_x, scene.render.resolution_y = old_x, old_y
scene.render.filepath = old_path
print(r"D:\project\blender_learning\renders\carthya_pose_eevee_check.png")
