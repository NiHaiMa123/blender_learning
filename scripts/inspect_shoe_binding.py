import bpy, json
from mathutils import Vector
def mods(o):
    return [dict(name=m.name,type=m.type,show=m.show_viewport,target=getattr(getattr(m,'object',None),'name',None)) for m in o.modifiers]
out={'file':bpy.data.filepath,'version':bpy.app.version_string,'mode':bpy.context.mode,'frame':bpy.context.scene.frame_current,'active':getattr(bpy.context.object,'name',None),'selected':[o.name for o in bpy.context.selected_objects]}
out['meshes']=[dict(name=o.name,n=len(o.data.vertices),parent=getattr(o.parent,'name',None),mods=mods(o),materials=[m.name if m else None for m in o.data.materials],keys=[(k.name,k.value) for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []) for o in bpy.context.scene.objects if o.type=='MESH' and (len(o.data.vertices)>300 or o.select_get()) and not o.rigid_body]
out['arms']=[dict(name=o.name,selected=[b.name for b in o.data.bones if getattr(b,'select',False)],bones=[dict(name=p.name,parent=getattr(p.parent,'name',None),head=list(p.head),tail=list(p.tail),rotation=list(p.rotation_quaternion),euler=list(p.rotation_euler),constraints=[dict(type=c.type,name=c.name,influence=c.influence) for c in p.constraints]) for p in o.pose.bones if any(s in p.name.lower() for s in ['足','ひざ','toe','ankle','foot','靴'])]) for o in bpy.context.scene.objects if o.type=='ARMATURE']
from pathlib import Path
Path('D:/project/blender_learning/validation/shoe_inspect_full.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
out['meshes']=[{**m,'keys':len(m['keys'])} for m in out['meshes'] if bpy.data.objects[m['name']].visible_get()]
out['arms']=[a for a in out['arms'] if a['name']==out['active']]
for a in out['arms']:
    a['bones']=[b for b in a['bones'] if not b['name'].startswith('_') and any(s in b['name'] for s in ['足首','足先','ひざD.','足ＩＫ'])]
print(json.dumps(out,ensure_ascii=False))

