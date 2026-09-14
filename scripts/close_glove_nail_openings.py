import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
root=Path('D:/project/blender_learning/validation/glove_fix_20260909');arm=bpy.data.objects['达妮娅_arm'];report={}
for s,n in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data)
 edges={e for e in bm.edges if e.is_boundary};loops=[]
 while edges:
  seed=edges.pop();stack=[seed];loop=[seed]
  while stack:
   e=stack.pop()
   for v in e.verts:
    for q in v.link_edges:
     if q in edges:edges.remove(q);loop.append(q);stack.append(q)
  loops.append(loop)
 wrist=arm.data.bones['手首.'+s];axis=(wrist.tail_local-wrist.head_local).normalized();filled=[]
 for loop in loops:
  verts={v for e in loop for v in e.verts};center=sum((v.co for v in verts),Vector())/len(verts)
  distance=(center-wrist.head_local).dot(axis)
  if distance>-.015:
   result=bmesh.ops.holes_fill(bm,edges=loop,sides=0)
   for f in result['faces']:f.material_index=21;f.smooth=True
   filled.extend(result['faces'])
 bmesh.ops.triangulate(bm,faces=filled);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 # Reproject UVs including newly closed fingertip/nail openings.
 raw=bpy.data.objects[n+'.001'].data;raw.calc_loop_triangles();coords=[Vector(v) for v in np.load(root/(n+'_retarget_world.npy'))]
 triangles=list(raw.loop_triangles);bvh=BVHTree.FromPolygons(coords,[list(t.vertices) for t in triangles],all_triangles=True)
 uv=o.data.uv_layers.active;sourceuv=raw.uv_layers.active
 for loop in o.data.loops:
  p=o.data.vertices[loop.vertex_index].co;loc,normal,ti,d=bvh.find_nearest(p);t=triangles[ti]
  out=barycentric_transform(loc,*[coords[i] for i in t.vertices],*[Vector((*sourceuv.data[i].uv,0)) for i in t.loops]);uv.data[loop.index].uv=out.xy
 report[n]={'boundary_components':len(loops),'closed_faces':len(filled),'faces_after':len(o.data.polygons)}
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:a.tag_redraw()
print(json.dumps(report,ensure_ascii=False))
