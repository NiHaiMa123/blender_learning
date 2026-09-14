import bpy,json,collections
from pathlib import Path
from mathutils import Vector
root=Path('D:/project/blender_learning/validation/glove_fix_20260909');root.mkdir(exist_ok=True)
out={'file':bpy.data.filepath,'mode':bpy.context.mode,'active':getattr(bpy.context.object,'name',None),'selected':[o.name for o in bpy.context.selected_objects],'frame':bpy.context.scene.frame_current}
def describe(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());co=[e.matrix_world@v.co for v in e.data.vertices]
 weights=collections.Counter(o.vertex_groups[g.group].name for v in o.data.vertices for g in v.groups if g.weight>0.001)
 return dict(name=o.name,n=len(o.data.vertices),parent=getattr(o.parent,'name',None),parent_type=o.parent_type,parent_bone=o.parent_bone,world=[list(r) for r in o.matrix_world],bounds=[[min(v[i] for v in co) for i in range(3)],[max(v[i] for v in co) for i in range(3)]],mods=[dict(name=m.name,type=m.type,target=getattr(getattr(m,'object',None),'name',None),visible=m.show_viewport) for m in o.modifiers],weights=weights,materials=[(i,m.name) for i,m in enumerate(o.data.materials) if m],keys=[(k.name,k.value) for k in o.data.shape_keys.key_blocks if k.value!=0] if o.data.shape_keys else [])
out['objects']=[describe(o) for o in bpy.context.scene.objects if o.type=='MESH' and ('手套' in o.name or o.name=='达妮娅_mesh')]
out['arms']=[dict(name=a.name,world=[list(r) for r in a.matrix_world],bones=[dict(name=p.name,parent=getattr(p.parent,'name',None),head=list(p.head),tail=list(p.tail),rest_head=list(p.bone.head_local),rest_tail=list(p.bone.tail_local),mode=p.rotation_mode,quat=list(p.rotation_quaternion),euler=list(p.rotation_euler),constraints=[(c.type,c.name,c.influence) for c in p.constraints]) for p in a.pose.bones if any(s in p.name for s in ['手首','指','腕','ひじ']) and not p.name.startswith('_')]) for a in bpy.context.scene.objects if a.type=='ARMATURE']
(root/'initial_inspection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({**out,'arms':[{'name':a['name'],'hand_bones':len(a['bones'])} for a in out['arms']]},ensure_ascii=False))
backup=root/'before_glove_fit.blend'
if not backup.exists():bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True)
bpy.ops.screen.screenshot(filepath=str(root/'before.png'))
