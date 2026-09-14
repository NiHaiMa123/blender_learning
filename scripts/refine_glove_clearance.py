import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/project/blender_learning/validation/glove_fix_20260909')
arm=bpy.data.objects['达妮娅_arm'];body=bpy.data.objects['达妮娅_mesh'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();be=body.evaluated_get(dg);bc=[v.co.copy() for v in be.data.vertices]
report={}
for s,n in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[n];vg=o.vertex_groups.get('指尖包覆余量') or o.vertex_groups.new(name='指尖包覆余量')
 distal={g.index for g in o.vertex_groups if g.name in [f+'３.'+s for f in ['人指','中指','薬指','小指']]+['親指２.'+s]}
 for v in o.data.vertices:
  w=sum(g.weight for g in v.groups if g.group in distal)
  if w>0:vg.add([v.index],min(1,w*1.5),'REPLACE')
 extra=o.modifiers.new('指尖包覆余量','DISPLACE');extra.direction='NORMAL';extra.strength=.0016;extra.mid_level=0;extra.vertex_group=vg.name
 o.modifiers.move(len(o.modifiers)-1,2)
 guard=o.modifiers.new('布料外侧防穿','SHRINKWRAP');guard.target=body;guard.wrap_method='NEAREST_SURFACEPOINT';guard.wrap_mode='OUTSIDE_SURFACE';guard.offset=.00065
 # Fit the wrist hardware radially out from the hand axis, keeping original detail.
 hw=bpy.data.objects[n+'_腕部装饰'];follow=hw.modifiers[0]
 with bpy.context.temp_override(object=hw,active_object=hw):
  if follow.is_bound:bpy.ops.object.surfacedeform_bind(modifier=follow.name)
 src=bpy.data.objects[n+'.001'].data;adj=[[] for v in src.vertices]
 for e in src.edges:
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
 hids=sorted({i for p in src.polygons if not any(i in fabric for i in p.vertices) for i in p.vertices})
 orig=np.load(root/(n+'_retarget_world.npy'))
 wrist=arm.pose.bones['手首.'+s];axis=(wrist.tail-wrist.head).normalized()
 bf=[list(p.vertices) for p in body.data.polygons if p.material_index==24 and all(body.data.vertices[i].co.x*(1 if s=='L' else -1)>.30 and .85<body.data.vertices[i].co.z<1.17 for i in p.vertices)]
 tree=BVHTree.FromPolygons(bc,bf)
 displacements=[]
 for v,idx in zip(hw.data.vertices,hids):
  p=Vector(orig[idx]);center=wrist.head+axis*(p-wrist.head).dot(axis);r=p-center;direction=r.normalized()
  hit,normal,fi,dist=tree.ray_cast(center+direction*.12,-direction,.14)
  if hit is not None:
   radius=(hit-center).dot(direction)+.0022
   q=center+direction*max(r.length,radius)
  else:q=p
  v.co=q;displacements.append((q-p).length)
 hw.data.update();bpy.context.view_layer.update()
 with bpy.context.temp_override(object=hw,active_object=hw):bpy.ops.object.surfacedeform_bind(modifier=follow.name)
 report[n]={'hardware_max_fit':max(displacements),'bound':follow.is_bound}
for a in bpy.context.screen.areas:a.tag_redraw()
print(json.dumps(report,ensure_ascii=False))
