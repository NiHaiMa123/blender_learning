import bpy
import json
from mathutils import Vector

cam = next((o for o in bpy.data.objects
            if o.type == "CAMERA" and o.data and o.data.name == "摄像机"), None)
if cam is None:
    raise RuntimeError("camera not found")

report = {"old_location": [round(v, 3) for v in cam.location]}

# pull back to include feet, aim at character center
cam.location = Vector((1.2, -12.6, 1.6))
target = Vector((1.0, -6.2, 0.85))
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = (target - cam.location).to_track_quat("-Z", "Y")

# refocus on character chest
chest = Vector((1.0, -7.0, 1.0))
cam.data.dof.focus_object = None
cam.data.dof.focus_distance = float((chest - cam.location).length)

report["new_location"] = [round(v, 3) for v in cam.location]
report["new_target"] = list(target)
report["new_focus"] = round(float(cam.data.dof.focus_distance), 3)
print(json.dumps(report, ensure_ascii=False, indent=1))
