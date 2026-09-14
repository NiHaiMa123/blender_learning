import bpy
import json
import math
from mathutils import Vector

empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE" and o.parent is not None and o.parent.name == empty.name), None)
bone = arm.pose.bones["上半身"]
head = arm.matrix_world @ bone.head
tail = arm.matrix_world @ bone.tail
axis = (tail - head).normalized()
vertical = Vector((0.0, 0.0, 1.0))
forward = (empty.matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()
horizontal_forward = Vector((forward.x, forward.y, 0.0)).normalized()
horizontal_axis = Vector((axis.x, axis.y, 0.0)).normalized()
angle_from_vertical = math.degrees(axis.angle(vertical))
forward_component = horizontal_axis.dot(horizontal_forward)
print(json.dumps({
    "waist_head": [round(float(v), 4) for v in head],
    "torso_axis": [round(float(v), 4) for v in axis],
    "angle_from_vertical_deg": round(float(angle_from_vertical), 3),
    "forward_component": round(float(forward_component), 4),
    "empty_yaw_deg": round(float(math.degrees(empty.rotation_euler.z)), 3),
}, ensure_ascii=False, indent=1))
