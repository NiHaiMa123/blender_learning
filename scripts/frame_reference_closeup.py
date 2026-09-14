import bpy, json
from mathutils import Vector
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
rep = {"old_loc":[round(v,3) for v in cam.location],"old_lens":round(float(cam.data.lens),2),
       "old_fstop":round(float(cam.data.dof.aperture_fstop),2),
       "old_focus":round(float(cam.data.dof.focus_distance),3)}
# close waist-up portrait like the reference: head top ~1.6 to knees ~0.5
cam.location = Vector((1.25, -9.40, 1.30))
target = Vector((1.00, -6.95, 1.02))
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = (target - cam.location).to_track_quat("-Z", "Y")
cam.data.lens = 50.0
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 1.4
cam.data.dof.focus_object = None
empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
arm = next((o for o in bpy.data.objects if o.type=="ARMATURE" and o.parent is not None and o.parent.name==empty.name), None)
face = arm.matrix_world @ arm.pose.bones["頭"].head
cam.data.dof.focus_distance = float((Vector((face.x, face.y, face.z)) - cam.location).length)
rep["new_loc"]=[round(v,3) for v in cam.location]
rep["new_target"]=list(target)
rep["new_lens"]=50.0
rep["new_fstop"]=round(float(cam.data.dof.aperture_fstop),2)
rep["face_world"]=[round(float(v),3) for v in face]
rep["new_focus"]=round(float(cam.data.dof.focus_distance),3)
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
