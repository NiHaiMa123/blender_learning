import bpy, os
path = r'D:\project\blender_learning\renders\carthya_keyframing_workspace.blend'
os.makedirs(os.path.dirname(path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)
print(path)
return_value = path
