import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
root=Path('D:/project/blender_learning/validation/glove_fix_20260909')
body=bpy.data.objects['达妮娅_mesh'];report={}
for s,name in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[name]
 assert len(o.data.vertices)==1987,'Already rebuilt; do not rerun'
 # Two large connected patches are the fabric; small patches are cuff hardware.
 adj=[[] for v in o.data.vertices]
 for e in o.data.edges:
  a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 seen=set();fabric=[]
 for i in range(len(adj)):
  if i in seen:continue
  stack=[i];seen.add(i);component=[]
  while stack:
   v=stack.pop();component.append(v)
   for j in adj[v]:
    if j not in seen:seen.add(j);stack.append(j)
  if len(component)>600:fabric.extend(component)
 vg=o.vertex_groups.get('手套布料_贴合') or o.vertex_groups.new(name='手套布料_贴合');vg.add(fabric,1.0,'REPLACE')
 sub=o.modifiers.new('拟合用细分','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=2;sub.render_levels=2
 sw=o.modifiers.new('拟合用外侧贴合','SHRINKWRAP');sw.target=body;sw.wrap_method='NEAREST_SURFACEPOINT';sw.wrap_mode='OUTSIDE_SURFACE';sw.offset=.0012;sw.vertex_group=vg.name
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 new=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 new.name=name+'_按素体拟合网格'
 o.data=new
 o.modifiers.remove(sub);o.modifiers.remove(sw)
 # Existing bind was made before fitting, so discard it on these two gloves only.
 for m in list(o.modifiers):
  if m.type=='SURFACE_DEFORM':o.modifiers.remove(m)
 bpy.context.view_layer.update()
 fitted=np.array([o.matrix_world@v.co for v in o.data.vertices]);np.save(root/(name+'_fitted_world.npy'),fitted)
 mod=o.modifiers.new('手套随手指变形_重新贴合','SURFACE_DEFORM');mod.target=bpy.data.objects['手套变形参考.'+s];mod.falloff=4
 with bpy.context.temp_override(object=o,active_object=o):bpy.ops.object.surfacedeform_bind(modifier=mod.name)
 assert mod.is_bound
 # Dynamic outside correction is AFTER surface following, preventing double motion.
 guard=o.modifiers.new('手套布料_动态防穿修正','SHRINKWRAP');guard.target=body;guard.wrap_method='NEAREST_SURFACEPOINT';guard.wrap_mode='OUTSIDE_SURFACE';guard.offset=.0012;guard.vertex_group=vg.name
 report[name]={'vertices':len(new.vertices),'polygons':len(new.polygons),'bound':mod.is_bound,'fabric_source_vertices':len(fabric),'clearance':guard.offset}
 o['手套修复']='以手腕及五指关节重新拟合；表面变形跟随素体手部，末端外侧贴合修正布料穿透。'
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:a.tag_redraw()
(root/'fit_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
