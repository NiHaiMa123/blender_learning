import bpy
import json

before_path = r"D:\project\blender_learning\renders\今汐_before_material_optimization.png"
after_path = r"D:\project\blender_learning\renders\今汐_after_material_optimization.png"
before = bpy.data.images.load(before_path, check_existing=False)
after = bpy.data.images.load(after_path, check_existing=False)
if tuple(before.size) != tuple(after.size):
    raise RuntimeError(f"Image sizes differ: {tuple(before.size)} vs {tuple(after.size)}")

before_pixels = list(before.pixels)
after_pixels = list(after.pixels)
diffs = [abs(a - b) for a, b in zip(before_pixels, after_pixels)]
print(json.dumps({
    "size": list(before.size),
    "mean_abs_diff": sum(diffs) / len(diffs),
    "max_abs_diff": max(diffs),
    "changed_channels": sum(value > 0.0001 for value in diffs),
}, indent=2))
bpy.data.images.remove(before)
bpy.data.images.remove(after)
