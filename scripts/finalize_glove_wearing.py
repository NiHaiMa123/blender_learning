import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
root=Path('D:/project/blender_learning/validation/glove_fix_20260909');body=bpy.data.objects['达妮娅_mesh'];arm=bpy.data.objects['达妮娅_arm']
for s,n in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[n]
 for name in ['指甲包覆防穿','指尖贴合精度']:
  m=o.modifiers.get(name)
  if m:o.modifiers.remove(m)
 o.modifiers['指尖包覆余量'].strength=.0005
 o.modifiers['布料外侧防穿'].target=bpy.data.objects['手套变形参考.'+s]
 hw=bpy.data.objects[n+'_腕部装饰'];hw.modifiers['腕部外侧防穿'].target=bpy.data.objects['手套变形参考.'+s]
 # Transfer only fabric UVs: do not paint the electronics texture onto the cloth.
 raw=bpy.data.objects[n+'.001'].data;adj=[[] for v in raw.vertices]
 for e in raw.edges:
  a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 seen=set();fabric=set()
 for i in range(len(adj)):
  if i in seen:continue
  stack=[i];seen.add(i);ids=[]
  while stack:
   j=stack.pop();ids.append(j)
   for k in adj[j]:
    if k not in seen:seen.add(k);stack.append(k)
  if len(ids)>600:fabric.update(ids)
 raw.calc_loop_triangles();tris=[t for t in raw.loop_triangles if all(i in fabric for i in t.vertices)];coords=[Vector(v) for v in np.load(root/(n+'_retarget_world.npy'))]
 bvh=BVHTree.FromPolygons(coords,[list(t.vertices) for t in tris],all_triangles=True);srcuv=raw.uv_layers.active;uv=o.data.uv_layers.active
 for l in o.data.loops:
  p=o.data.vertices[l.vertex_index].co;loc,norm,ti,d=bvh.find_nearest(p);t=tris[ti]
  q=barycentric_transform(loc,*[coords[i] for i in t.vertices],*[Vector((*srcuv.data[i].uv,0)) for i in t.loops]);uv.data[l.index].uv=q.xy
 o.data.update()
# Reversible clothing mask: keep the actual hand and nail mesh untouched, and hide
# only the parts fully enclosed by the worn gloves. All motion uses unmasked proxies.
vg=body.vertex_groups.get('手套穿戴_内部皮肤与指甲') or body.vertex_groups.new(name='手套穿戴_内部皮肤与指甲')
maskids=set()
for s in ['L','R']:
 wrist=arm.data.bones['手首.'+s];axis=(wrist.tail_local-wrist.head_local).normalized();sign=1 if s=='L' else -1
 for p in body.data.polygons:
  if p.material_index not in [24,25]:continue
  for i in p.vertices:
   v=body.data.vertices[i]
   if sign*v.co.x>.30 and .85<v.co.z<1.17 and (v.co-wrist.head_local).dot(axis)>-.020:maskids.add(i)
vg.add(sorted(maskids),1,'REPLACE')
m=body.modifiers.new('穿戴手套_隐藏内部手部','MASK');m.vertex_group=vg.name;m.invert_vertex_group=True
arm['穿戴手套']=1.0;arm.id_properties_ui('穿戴手套').update(min=0,max=1,description='1=穿戴双手套并隐藏内部皮肤和指甲；0=脱下双手套并显示完整原手。')
def driver(obj,path,expression):
 f=obj.driver_add(path);d=f.driver;d.type='SCRIPTED';v=d.variables.new();v.name='worn';v.type='SINGLE_PROP';v.targets[0].id=arm;v.targets[0].data_path='["穿戴手套"]';d.expression=expression
driver(m,'show_viewport','worn > 0.5');driver(m,'show_render','worn > 0.5')
for n in ['右手套','左手套','右手套_腕部装饰','左手套_腕部装饰']:
 o=bpy.data.objects[n];driver(o,'hide_viewport','worn < 0.5');driver(o,'hide_render','worn < 0.5')
bpy.data.objects['达妮娅_红色毛茸袖形态_arm'].hide_set(True)
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:a.tag_redraw()
(root/'wearing_setup.json').write_text(json.dumps({'masked_vertices':len(maskids),'toggle_armature':arm.name,'toggle':'穿戴手套','body_geometry_edited':False,'cutoff':-.020},ensure_ascii=False,indent=2),encoding='utf8')
print('Wear toggle installed; covered hand mesh preserved non-destructively.',len(maskids))
