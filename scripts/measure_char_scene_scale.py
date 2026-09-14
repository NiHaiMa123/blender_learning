import bpy, json
from mathutils import Vector
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
mesh = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
out = {}
out["cam_loc"] = [round(v,3) for v in cam.location]
out["cam_lens"] = round(float(cam.data.lens),2)
out["cam_sensor"] = round(float(cam.data.sensor_width),2)
out["cam_dof"] = [bool(cam.data.dof.use_dof), round(float(cam.data.dof.focus_distance),3)]
if empty: out["char_loc"] = [round(v,3) for v in empty.location]
if mesh:
    ws = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
    xs=[v.x for v in ws]; ys=[v.y for v in ws]; zs=[v.z for v in ws]
    out["char_bbox_world"] = {"x":[round(min(xs),3),round(max(xs),3)],"y":[round(min(ys),3),round(max(ys),3)],"z":[round(min(zs),3),round(max(zs),3)]}
    out["char_height"] = round(max(zs)-min(zs),3)
    chest = Vector((empty.location.x, empty.location.y, 1.0))
    out["dist_cam_chest"] = round(float((chest-cam.location).length),3)
# scene props scale: railing posts / bench / lamp
cands=[]
for o in bpy.data.objects:
    n=o.name
    if any(k in n for k in ["栏","杆","柱","凳","椅","Bench"," bench","Railing","Post","路灯","点光"]):
        try:
            ws2=[o.matrix_world @ v.co for v in o.data.vertices] if hasattr(o,"data") and hasattr(o.data,"vertices") else []
            if ws2:
                zs2=[v.z for v in ws2]
                cands.append({"name":n,"z":[round(min(zs2),3),round(max(zs2),3)],"h":round(max(zs2)-min(zs2),3),"loc":[round(v,3) for v in o.location]})
        except Exception:
            pass
out["props"]=cands[:20]
print(json.dumps(out, ensure_ascii=False, indent=1))
