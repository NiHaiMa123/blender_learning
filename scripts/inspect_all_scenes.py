import bpy
import json

rows = []
for scene in bpy.data.scenes:
    rows.append({
        "name": scene.name,
        "camera": scene.camera.name if scene.camera else None,
        "engine": scene.render.engine,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "objects": len(scene.objects),
        "camera_location": list(scene.camera.location) if scene.camera else None,
        "camera_rotation": list(scene.camera.rotation_euler) if scene.camera else None,
    })
print(json.dumps({"context": bpy.context.scene.name, "scenes": rows}, ensure_ascii=False, indent=2))
