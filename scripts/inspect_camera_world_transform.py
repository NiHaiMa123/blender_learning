import bpy
import json

camera = bpy.context.scene.camera
print(json.dumps({
    "name": camera.name,
    "parent": camera.parent.name if camera.parent else None,
    "location": list(camera.location),
    "rotation": list(camera.rotation_euler),
    "matrix_world": [[round(float(value), 5) for value in row] for row in camera.matrix_world],
    "data_type": camera.data.type,
    "lens": camera.data.lens,
    "shift": [camera.data.shift_x, camera.data.shift_y],
    "clip": [camera.data.clip_start, camera.data.clip_end],
}, ensure_ascii=False, indent=2))
