import bpy,json
from mathutils.bvhtree import BVHTree
body=bpy.data.objects['达妮娅_mesh'];report={}
for s,n in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[n];bf=[list(p.vertices) for p in body.data.polygons if p.material_index==25 and all(body.data.vertices[i].co.x*(1 if s=='L' else -1)>.30 and .85<body.data.vertices[i].co.z<1.17 for i in p.vertices)]
 out=[]
 for strength in [.0016,.0025,.0035,.005]:
  o.modifiers['指尖包覆余量'].strength=strength;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();be=body.evaluated_get(dg);e=o.evaluated_get(dg)
  bt=BVHTree.FromPolygons([v.co.copy() for v in be.data.vertices],bf);gt=BVHTree.FromPolygons([v.co.copy() for v in e.data.vertices],[list(p.vertices) for p in e.data.polygons[:len(o.data.polygons)]])
  c=len(bt.overlap(gt));out.append((strength,c))
  if c==0:break
 report[n]=out
print(json.dumps(report,ensure_ascii=False))
