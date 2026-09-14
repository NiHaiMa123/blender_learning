import bpy, json
from mathutils import Vector
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
cam.location = Vector((1.1, -11.4, 1.5))
target = Vector((1.0, -6.9, 0.78))
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = (target - cam.location).to_track_quat("-Z", "Y")
cam.data.lens = 50.0
chest = Vector((1.0, -7.0, 1.0))
cam.data.dof.focus_object = None
cam.data.dof.focus_distance = float((chest - cam.location).length)
out={"new_loc":[round(v,3) for v in cam.location],"new_lens":50.0,"new_focus":round(float(cam.data.dof.focus_distance),3)}
bpy.ops.wm.save_mainfile()
print(json.dumps(out, ensure_ascii=False, indent=1))
