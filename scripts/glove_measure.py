import bpy,json,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
root=Path('D:/project/blender_learning/validation/glove_fix_20260909')
body=bpy.data.objects['达妮娅_mesh'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
be=body.evaluated_get(dg);bv=[be.matrix_world@v.co for v in be.data.vertices]
out={}
for s,n in [('R','右手套'),('L','左手套')]:
 sign=1 if s=='L' else -1
 ids=[p.index for p in body.data.polygons if p.material_index in [24,25] and all(sign*body.data.vertices[i].co.x>.30 and .85<body.data.vertices[i].co.z<1.17 for i in p.vertices)]
 bf=[list(body.data.polygons[i].vertices) for i in ids];bt=BVHTree.FromPolygons(bv,bf)
 o=bpy.data.objects[n];e=o.evaluated_get(dg);gv=[e.matrix_world@v.co for v in e.data.vertices];gf=[list(p.vertices) for p in e.data.polygons]
 overlaps=bt.overlap(BVHTree.FromPolygons(gv,gf));gi=o.vertex_groups['手套布料_贴合'].index
 counts={'fabric':0,'hardware':0};negative=[]
 for bi,fi in overlaps:
  isfabric=any(any(g.group==gi and g.weight>.5 for g in o.data.vertices[i].groups) for i in e.data.polygons[fi].vertices)
  counts['fabric' if isfabric else 'hardware']+=1
 for i,v in enumerate(gv):
  loc,norm,fi,dist=bt.find_nearest(v)
  signed=(v-loc).dot(norm)
  if signed<-.00005:negative.append((i,signed))
 out[n]={'overlap_pairs':len(overlaps),'by_type':counts,'negative_vertices':len(negative),'worst_inside':min((d for i,d in negative),default=0)}
 (root/(s+'_overlaps.json')).write_text(json.dumps({'body_faces':ids,'overlaps':overlaps,'negative':negative}),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))
(root/'current_clearance.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
