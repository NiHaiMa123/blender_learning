import bpy, json
from mathutils import Vector
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
report = {"old_loc":[round(v,3) for v in cam.location],"old_lens":round(float(cam.data.lens),2)}
# closer fullbody portrait: char fills ~75-80% frame height
cam.location = Vector((1.1, -11.1, 1.45))
target = Vector((1.0, -6.85, 0.80))
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = (target - cam.location).to_track_quat("-Z", "Y")
cam.data.lens = 52.0
chest = Vector((1.0, -7.0, 1.0))
cam.data.dof.focus_object = None
cam.data.dof.focus_distance = float((chest - cam.location).length)
report["new_loc"]=[round(v,3) for v in cam.location]
report["new_target"]=list(target)
report["new_lens"]=52.0
report["new_focus"]=round(float(cam.data.dof.focus_distance),3)
bpy.ops.wm.save_mainfile()
print(json.dumps(report, ensure_ascii=False, indent=1))
