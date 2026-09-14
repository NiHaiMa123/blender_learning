import bpy
import json
from mathutils import Vector


scene = bpy.context.scene
mesh_objects = [obj for obj in scene.objects if obj.type == "MESH"]
points = []
for obj in mesh_objects:
    if not obj.bound_box:
        continue
    points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)

mins = [min(point[index] for point in points) for index in range(3)]
maxs = [max(point[index] for point in points) for index in range(3)]
report = {
    "scene": scene.name,
    "active_camera": scene.camera.name if scene.camera else None,
    "bounds": {"min": mins, "max": maxs, "center": [(lo + hi) * 0.5 for lo, hi in zip(mins, maxs)]},
    "cameras": [],
}
for camera in [obj for obj in scene.objects if obj.type == "CAMERA"]:
    report["cameras"].append({
        "name": camera.name,
        "location": list(camera.location),
        "rotation": list(camera.rotation_euler),
        "lens": camera.data.lens,
        "sensor_fit": camera.data.sensor_fit,
        "constraints": [constraint.type for constraint in camera.constraints],
    })
print(json.dumps(report, ensure_ascii=False, indent=2))
