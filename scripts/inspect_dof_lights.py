import bpy, json
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
d = cam.data
out = {"cam_loc":[round(v,3) for v in cam.location],"lens":round(float(d.lens),2),
 "dof":{"use":bool(d.dof.use_dof),"focus_distance":round(float(d.dof.focus_distance),3),
 "aperture":round(float(d.dof.aperture_fstop),3),"aperture_blades":int(getattr(d.dof,"aperture_blades",0)),
 "focus_object":d.dof.focus_object.name if d.dof.focus_object else None}}
lights=[]
for o in bpy.data.objects:
    if o.type=="LIGHT":
        dd=o.data
        lights.append({"name":o.name,"type":dd.type,"energy":round(float(dd.energy),1),
         "color":[round(float(c),3) for c in dd.color],"loc":[round(v,2) for v in o.location],
         "hide_render":bool(o.hide_render),"parent":o.parent.name if o.parent else None,
         "in_rig":False,"in_scene":False})
scene_coll=bpy.data.collections.get("场景"); rig_coll=bpy.data.collections.get("人物灯光（b站搜三分仪打光教程）")
keep=set()
for c in [c for c in (scene_coll,rig_coll) if c]:
    for sub in [c]+list(c.children_recursive): keep.update(sub.objects)
for L in lights:
    o=bpy.data.objects.get(L["name"])
    L["kept_in_render"]=o in keep
lights.sort(key=lambda l:(l["hide_render"],-l["energy"]))
out["lights"]=lights
vols=[]
for m in bpy.data.materials:
    if m.use_nodes and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type=="PRINCIPLED_VOLUME":
                inp={}
                for s in ("Density","Anisotropy","Absorption Color"):
                    try: v=n.inputs[s].default_value; inp[s]=round(float(v),4) if isinstance(v,float) else str(v)
                    except Exception: pass
                vols.append({"mat":m.name,"node":n.name,"inputs":inp})
out["volumes"]=vols
print(json.dumps(out, ensure_ascii=False, indent=1))
