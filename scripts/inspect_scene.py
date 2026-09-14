import bpy
import json


def world_bounds(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH" or not obj.bound_box:
            continue
        points.extend(obj.matrix_world @ obj_corner for obj_corner in map(lambda c: __import__('mathutils').Vector(c), obj.bound_box))
    if not points:
        return None
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return {"min": [round(v, 3) for v in mins], "max": [round(v, 3) for v in maxs]}


armatures = []
for arm in [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]:
    descendants = list(arm.children_recursive)
    meshes = [o for o in descendants if o.type == "MESH"]
    armatures.append({
        "name": arm.name,
        "location": [round(v, 3) for v in arm.location],
        "rotation": [round(v, 3) for v in arm.rotation_euler],
        "scale": [round(v, 3) for v in arm.scale],
        "mesh_count": len(meshes),
        "mesh_names": [o.name for o in meshes[:30]],
        "bounds": world_bounds(meshes),
    })

cameras = []
for obj in [o for o in bpy.context.scene.objects if o.type == "CAMERA"]:
    cameras.append({
        "name": obj.name,
        "location": [round(v, 3) for v in obj.location],
        "rotation": [round(v, 3) for v in obj.rotation_euler],
        "lens": obj.data.lens,
        "sensor_width": obj.data.sensor_width,
        "dof": obj.data.dof.use_dof,
        "focus_object": obj.data.dof.focus_object.name if obj.data.dof.focus_object else None,
        "focus_distance": obj.data.dof.focus_distance,
        "fstop": obj.data.dof.aperture_fstop,
    })

lights = []
for obj in [o for o in bpy.context.scene.objects if o.type == "LIGHT"]:
    lights.append({
        "name": obj.name,
        "type": obj.data.type,
        "energy": obj.data.energy,
        "color": [round(v, 3) for v in obj.data.color],
        "location": [round(v, 3) for v in obj.location],
        "rotation": [round(v, 3) for v in obj.rotation_euler],
    })

collections = sorted(
    ({"name": c.name, "objects": len(c.all_objects)} for c in bpy.data.collections),
    key=lambda item: item["objects"],
    reverse=True,
)

scene = bpy.context.scene
report = {
    "filepath": bpy.data.filepath,
    "active_camera": scene.camera.name if scene.camera else None,
    "render_engine": scene.render.engine,
    "resolution": [scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage],
    "frame": scene.frame_current,
    "world_color": list(scene.world.color) if scene.world else None,
    "armatures": armatures,
    "cameras": cameras,
    "lights": lights,
    "largest_collections": collections[:25],
}
print(json.dumps(report, ensure_ascii=False, indent=2))
