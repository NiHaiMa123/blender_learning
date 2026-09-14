import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
root=Path('D:/project/blender_learning/validation/glove_fix_20260909');body=bpy.data.objects['达妮娅_mesh']
for s,n in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[n];o.modifiers['布料外侧防穿'].wrap_mode='OUTSIDE'
 hw=bpy.data.objects[n+'_腕部装饰'];raw=bpy.data.objects[n+'.001'].data
 adj=[[] for v in raw.vertices]
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
 hids=sorted({i for p in raw.polygons if not any(i in fabric for i in p.vertices) for i in p.vertices})
 coords=np.load(root/(n+'_retarget_world.npy'));assert len(hw.data.vertices)==len(hids)
 for m in list(hw.modifiers):hw.modifiers.remove(m)
 for v,i in zip(hw.data.vertices,hids):v.co=Vector(coords[i])
 hw.data.update()
 sub=hw.modifiers.new('腕部细分贴合','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=2;sub.render_levels=2
 sw=hw.modifiers.new('腕部外侧贴合','SHRINKWRAP');sw.target=body;sw.wrap_method='NEAREST_SURFACEPOINT';sw.wrap_mode='OUTSIDE';sw.offset=.0018
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();mesh=bpy.data.meshes.new_from_object(hw.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
 hw.data=mesh;hw.modifiers.remove(sub);hw.modifiers.remove(sw)
 m=hw.modifiers.new('腕部装饰随手变形','SURFACE_DEFORM');m.target=bpy.data.objects['手套变形参考.'+s]
 with bpy.context.temp_override(object=hw,active_object=hw):bpy.ops.object.surfacedeform_bind(modifier=m.name)
 sw=hw.modifiers.new('腕部外侧防穿','SHRINKWRAP');sw.target=body;sw.wrap_method='NEAREST_SURFACEPOINT';sw.wrap_mode='OUTSIDE';sw.offset=.0012
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:a.tag_redraw()
print('Outside-only guards enabled; cuff original detail restored and fitted.')
