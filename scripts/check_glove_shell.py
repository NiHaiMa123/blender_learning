import bpy,json,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
root=Path('D:/project/blender_learning/validation/glove_fix_20260909')
body=bpy.data.objects['达妮娅_mesh'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();be=body.evaluated_get(dg);bc=[v.co.copy() for v in be.data.vertices]
report={}
for s,n in [('R','右手套'),('L','左手套')]:
 out={};sign=1 if s=='L' else -1
 fs={mat:[p for p in body.data.polygons if p.material_index==mat and all(sign*body.data.vertices[i].co.x>.30 and .85<body.data.vertices[i].co.z<1.17 for i in p.vertices)] for mat in [24,25]}
 bt={mat:BVHTree.FromPolygons(bc,[list(p.vertices) for p in faces]) for mat,faces in fs.items()}
 for name in [n,n+'_腕部装饰']:
  o=bpy.data.objects[name];e=o.evaluated_get(dg);gc=[e.matrix_world@v.co for v in e.data.vertices];gf=[list(p.vertices) for p in e.data.polygons]
  gt=BVHTree.FromPolygons(gc,gf)
  out[name]={str(mat):len(t.overlap(gt)) for mat,t in bt.items()}
 nd=[]
 for i in {i for p in fs[25] for i in p.vertices}:
  q,norm,fi,dist=bt[24].find_nearest(bc[i]);nd.append((bc[i]-q).dot(norm))
 out['nail_protrusion_quantiles']=np.quantile(nd,[0,.5,.9,1]).tolist()
 report[s]=out
print(json.dumps(report,ensure_ascii=False));(root/'shell_clearance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
