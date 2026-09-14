import bpy
import os

path = r"D:\project\blender_learning\renders\今汐_before_material_optimization.blend"
os.makedirs(os.path.dirname(path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)
print(path)
