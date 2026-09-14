import bpy
import json

cam = next((o for o in bpy.data.objects
            if o.type == "CAMERA" and o.data and o.data.name == "摄像机"), None)
mesh = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
d = cam.data.dof
report = {
    "use_dof": bool(d.use_dof),
    "focus_object": d.focus_object.name if d.focus_object else None,
    "focus_distance": round(float(d.focus_distance), 3),
    "aperture": round(float(d.aperture_fstop), 3),
}
# aim focus at character chest
chest = mesh.matrix_world @ mesh.data.vertices[0].co  # placeholder
import mathutils
ws = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
chest = mathutils.Vector((
    sum(v.x for v in ws) / len(ws),
    sum(v.y for v in ws) / len(ws),
    1.1,
))
dist = (chest - cam.location).length
d.focus_object = None
d.focus_distance = float(dist)
report["new_focus_distance"] = round(float(dist), 3)
report["facing_hint"] = {
    "mesh_world_y_extent": [round(min(v.y for v in ws), 3), round(max(v.y for v in ws), 3)],
}
print(json.dumps(report, ensure_ascii=False, indent=1))
