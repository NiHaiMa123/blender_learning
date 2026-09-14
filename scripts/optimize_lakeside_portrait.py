import bpy, json
from mathutils import Vector
rep = {}
# 1. DOF: f/0.5 -> f/4.0, keep focus on chest
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
rep["old_fstop"] = round(float(cam.data.dof.aperture_fstop),2)
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 4.0
cam.data.dof.focus_object = None
chest = Vector((1.0,-7.0,1.0))
cam.data.dof.focus_distance = float((chest - cam.location).length)
rep["new_fstop"] = 4.0
rep["new_focus"] = round(float(cam.data.dof.focus_distance),3)
# 2. Skin: press translucency, keep gloss
skin = bpy.data.materials.get("皮肤")
p = skin.node_tree.nodes.get("Skin Principled")
rep["old_sss"] = [round(float(p.inputs["Subsurface Weight"].default_value),3),
                  round(float(p.inputs["Subsurface Scale"].default_value),4),
                  [round(float(x),3) for x in p.inputs["Subsurface Radius"].default_value]]
p.inputs["Subsurface Weight"].default_value = 0.30
p.inputs["Subsurface Scale"].default_value = 0.035
p.inputs["Subsurface Radius"].default_value = (0.6, 0.28, 0.2)
p.inputs["Roughness"].default_value = 0.28
rep["new_sss"] = [0.30, 0.035, [0.6,0.28,0.2]]
# 3. Tame rig backlights that blast through the body (they follow CHAR_POS via parent)
for n, e in (("背光.001",1200.0),("顶光.001",700.0),("左测光.001",450.0)):
    o = bpy.data.objects.get(n)
    if o is not None:
        rep[f"old_{n}"] = round(float(o.data.energy),1)
        o.data.energy = e
        rep[f"new_{n}"] = e
# 4. Face fill: soft warm area from camera side, kept in render via rig collection
rig = bpy.data.collections.get("人物灯光（b站搜三分仪打光教程）")
root = bpy.data.objects.get("空物体.027")
fill = bpy.data.objects.get("Codex_Face_Fill")
if fill is None:
    bpy.ops.object.light_add(type="AREA", location=(1.0,-9.6,1.55))
    fill = bpy.context.active_object
    fill.name = "Codex_Face_Fill"
    fill.data.name = "Codex_Face_Fill"
    if rig is not None:
        for c in list(fill.users_collection):
            try: c.objects.unlink(fill)
            except Exception: pass
        rig.objects.link(fill)
fill.location = (1.0,-9.6,1.55)
fill.parent = root
fill.matrix_parent_inverse = root.matrix_world.inverted()
fill.data.energy = 80.0
fill.data.color = (1.0, 0.85, 0.70)
fill.data.shape = "RECTANGLE"
fill.data.size = 1.2
try: fill.data.size_y = 0.8
except Exception: pass
# aim at face
face = Vector((1.0,-7.0,1.35))
fill.rotation_mode = "QUATERNION"
fill.rotation_quaternion = (face - Vector(fill.matrix_world.translation)).to_track_quat("-Z","Y")
rep["face_fill"] = {"energy":80.0,"loc":[1.0,-9.6,1.55]}
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
