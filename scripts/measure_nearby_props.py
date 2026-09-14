import bpy, json
from mathutils import Vector
char = Vector((1.0,-7.0,0.8))
rows=[]
for o in bpy.data.objects:
    if o.type=="MESH" and any(k in o.name for k in ["栏","杆","Bench","长椅","椅","Railing","Post","柱","灯","Lamp","路灯","Stone","石","Tree","树","桥"]):
        try:
            d=(o.location-char).length
            if d<25:
                ws=[o.matrix_world @ v.co for v in o.data.vertices]
                zs=[v.z for v in ws]
                rows.append({"name":o.name,"dist":round(float(d),2),"loc":[round(v,2) for v in o.location],"h":round(float(max(zs)-min(zs)),3)})
        except Exception:
            pass
rows.sort(key=lambda r:r["dist"])
print(json.dumps(rows[:25], ensure_ascii=False, indent=1))
