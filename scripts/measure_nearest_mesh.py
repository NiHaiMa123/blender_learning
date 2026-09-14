import bpy, json
from mathutils import Vector
char = Vector((1.0,-7.0,0.8))
rows=[]
for o in bpy.data.objects:
    if o.type=="MESH" and o.visible_get():
        try:
            d=(Vector((o.location.x,o.location.y,o.location.z))-char).length
            if d<10 and "今汐" not in o.name and "Armature" not in o.name:
                ws=[o.matrix_world @ v.co for v in o.data.vertices]
                zs=[v.z for v in ws]
                rows.append({"name":o.name,"dist":round(float(d),2),"h":round(float(max(zs)-min(zs)),3),"verts":len(o.data.vertices)})
        except Exception as e:
            pass
rows.sort(key=lambda r:r["dist"])
print(json.dumps(rows[:30], ensure_ascii=False, indent=1))
