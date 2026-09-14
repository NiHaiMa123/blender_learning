import bpy,json,collections
from mathutils.bvhtree import BVHTree
body=bpy.data.objects['达妮娅_mesh'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();be=body.evaluated_get(dg);bc=[v.co.copy() for v in be.data.vertices]
for s,n in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[n];e=o.evaluated_get(dg);gc=[v.co.copy() for v in e.data.vertices];gf=[list(p.vertices) for p in e.data.polygons];gt=BVHTree.FromPolygons(gc,gf)
 for mat in [24,25]:
  fs=[list(p.vertices) for p in body.data.polygons if p.material_index==mat and all(body.data.vertices[i].co.x*(1 if s=='L' else -1)>.30 and .85<body.data.vertices[i].co.z<1.17 for i in p.vertices)]
  pairs=BVHTree.FromPolygons(bc,fs).overlap(gt)
  print(n,mat,'OUTER',sum(1 for a,b in pairs if b<len(o.data.polygons)),'INNER_RIM',sum(1 for a,b in pairs if b>=len(o.data.polygons)))
a=bpy.data.objects['达妮娅_arm']
for n in ['手首.R','人指１.R','人指２.R','人指３.R','人指握.R','親指１.R']:
 p=a.pose.bones[n];print(n,p.rotation_mode,list(p.rotation_quaternion), 'axes',list(p.matrix.to_3x3().col[0]),list(p.matrix.to_3x3().col[1]),[(c.type,c.name) for c in p.constraints])
