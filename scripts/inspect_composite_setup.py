import bpy
import json
from mathutils import Vector

report = {}

# scene camera
cam = next((o for o in bpy.data.objects
            if o.type == "CAMERA" and o.data and o.data.name == "摄像机"), None)
report["camera"] = {"name": cam.name, "loc": [round(v, 3) for v in cam.location],
                    "lens": round(float(cam.data.lens), 2)} if cam else None

# character root structure
empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
arm = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_arm")
mesh = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
report["root"] = {
    "empty_loc": [round(v, 3) for v in empty.location] if empty else None,
    "empty_children": [c.name for c in empty.children] if empty else None,
    "arm_parent": arm.parent.name if arm and arm.parent else None,
    "mesh_parent": mesh.parent.name if mesh and mesh.parent else None,
    "arm_loc": [round(v, 3) for v in arm.location] if arm else None,
}
# character world height
if mesh:
    ws = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
    report["char_world_bbox"] = {
        "x": [round(min(v.x for v in ws), 3), round(max(v.x for v in ws), 3)],
        "y": [round(min(v.y for v in ws), 3), round(max(v.y for v in ws), 3)],
        "z": [round(min(v.z for v in ws), 3), round(max(v.z for v in ws), 3)],
    }

# ground height via raycast down at candidate spots on the path
deps = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene
grounds = {}
for key, (x, y) in {"center_path": (0.0, 8.0), "near_bench": (-1.5, 10.0),
                     "mid_path": (0.5, 14.0)}.items():
    hit, loc, *_ = scene.ray_cast(deps, Vector((x, y, 5.0)), Vector((0, 0, -1)))
    grounds[key] = {"hit": hit,
                    "z": round(float(loc.z), 3) if hit else None,
                    "hit_obj": None}
    if hit:
        # find what was hit is expensive; skip
        pass
report["grounds"] = grounds

# author character-lighting rig (unlinked)
rig = bpy.data.collections.get("人物灯光（b站搜三分仪打光教程）")
report["char_light_rig"] = ([o.name for o in rig.all_objects][:20]
                            if rig else None)

# our studio lights (to hide during composite)
studio = ["Key_Soft", "Rim_Cool", "Fill_Front", "Skin_Fill", "EyeLight",
          "Overhead_Soft", "Side_Fill_Left", "Back_Fill_Warm",
          "Metal_Strip_Key", "Metal_Strip_Rim", "Leg_Fill_Front",
          "Leg_Fill_Right", "Leg_Fill_Left", "Leg_Fill_Ring", "Practical_Warm"]
report["studio_lights"] = [n for n in studio if n in bpy.data.objects]

print(json.dumps(report, ensure_ascii=False, indent=1))
