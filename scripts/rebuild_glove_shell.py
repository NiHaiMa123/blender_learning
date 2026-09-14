"""Rebuild glove fabric on the actual hand topology; transfer the original UV art."""
import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
root=Path('D:/project/blender_learning/validation/glove_fix_20260909')
body=bpy.data.objects['达妮娅_mesh'];arm=bpy.data.objects['达妮娅_arm']
report={}
for s,name in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[name];template=bpy.data.objects[name+'.001'];raw=template.data
 sourcecoords=[Vector(v) for v in np.load(root/(name+'_retarget_world.npy'))]
 # Get the two original fabric panels, excluding wrist electronics and trim.
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
 raw.calc_loop_triangles();triangles=[t for t in raw.loop_triangles if all(i in fabric for i in t.vertices)]
 sourcebvh=BVHTree.FromPolygons(sourcecoords,[list(t.vertices) for t in triangles],all_triangles=True)
 sourceuv=raw.uv_layers.active
 wrist=arm.data.bones['手首.'+s];axis=(wrist.tail_local-wrist.head_local).normalized()
 cutoff=-.023
 # Body and glove now use exactly the same rest geometry and vertex weights.
 faces=[p for p in body.data.polygons if p.material_index==24 and all(v.co.x*(1 if s=='L' else -1)>.30 and .85<v.co.z<1.17 and (v.co-wrist.head_local).dot(axis)>cutoff-.012 for v in [body.data.vertices[i] for i in p.vertices])]
 ids=sorted({i for p in faces for i in p.vertices});mapping={i:j for j,i in enumerate(ids)}
 mesh=bpy.data.meshes.new(name+'_贴合素体布料')
 mesh.from_pydata([body.data.vertices[i].co.copy() for i in ids],[],[[mapping[i] for i in p.vertices] for p in faces]);mesh.update()
 # Set weights before bisect so newly created boundary vertices interpolate them.
 for m in list(o.modifiers):o.modifiers.remove(m)
 o.data=mesh;o.parent=arm;o.parent_type='OBJECT';o.parent_bone='';o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=body.matrix_world.copy()
 o.vertex_groups.clear()
 for vg in body.vertex_groups:o.vertex_groups.new(name=vg.name)
 for old,new in mapping.items():
  for g in body.data.vertices[old].groups:
   if body.vertex_groups[g.group].name in arm.data.bones:o.vertex_groups[g.group].add([new],g.weight,'REPLACE')
 bm=bmesh.new();bm.from_mesh(mesh)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=wrist.head_local+axis*cutoff,plane_no=axis,clear_inner=True,clear_outer=False,dist=1e-7)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
 for m in raw.materials:mesh.materials.append(m)
 uv=mesh.uv_layers.new(name='原手套纹理_转移')
 for loop in mesh.loops:
  p=mesh.vertices[loop.vertex_index].co
  loc,norm,ti,dist=sourcebvh.find_nearest(p);t=triangles[ti]
  a,b,c=[sourcecoords[i] for i in t.vertices]
  ua,ub,uc=[Vector((*sourceuv.data[i].uv,0.0)) for i in t.loops]
  out=barycentric_transform(loc,a,b,c,ua,ub,uc)
  uv.data[loop.index].uv=out.xy
 for p in mesh.polygons:p.material_index=21;p.use_smooth=True
 am=o.modifiers.new('与素体手部一致的骨骼权重','ARMATURE');am.object=arm;am.use_deform_preserve_volume=False
 dis=o.modifiers.new('手套布料厚度间隙','DISPLACE');dis.direction='NORMAL';dis.strength=.0015;dis.mid_level=0
 solid=o.modifiers.new('手套边缘厚度','SOLIDIFY');solid.thickness=.0003;solid.offset=-1;solid.use_rim=True
 # Keep the imported wrist hardware, UVs, and material slots as separate geometry.
 hfaces=[p for p in raw.polygons if not any(i in fabric for i in p.vertices)]
 hids=sorted({i for p in hfaces for i in p.vertices});hmapping={i:j for j,i in enumerate(hids)}
 hm=bpy.data.meshes.new(name+'_原腕部装饰')
 hm.from_pydata([sourcecoords[i] for i in hids],[],[[hmapping[i] for i in p.vertices] for p in hfaces]);hm.update()
 for m in raw.materials:hm.materials.append(m)
 huv=hm.uv_layers.new(name=sourceuv.name)
 for p,old in zip(hm.polygons,hfaces):
  p.material_index=old.material_index;p.use_smooth=old.use_smooth
  for li,oli in zip(p.loop_indices,old.loop_indices):huv.data[li].uv=sourceuv.data[oli].uv
 hw=bpy.data.objects.new(name+'_腕部装饰',hm);o.users_collection[0].objects.link(hw);hw.parent=arm;hw.matrix_world=Matrix.Identity(4)
 # Static outside fitting of cuff hardware before binding.
 sw=hw.modifiers.new('腕部贴合','SHRINKWRAP');sw.target=body;sw.wrap_method='NEAREST_SURFACEPOINT';sw.wrap_mode='OUTSIDE_SURFACE';sw.offset=.0018
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 fitted=bpy.data.meshes.new_from_object(hw.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);hw.data=fitted;hw.modifiers.remove(sw)
 follow=hw.modifiers.new('腕部装饰跟随手腕','SURFACE_DEFORM');follow.target=bpy.data.objects['手套变形参考.'+s]
 with bpy.context.temp_override(object=hw,active_object=hw):bpy.ops.object.surfacedeform_bind(modifier=follow.name)
 assert follow.is_bound
 o['手套修复']='布料使用素体手部拓扑和骨骼权重，原红色手套纹理转移；骨骼变形后沿法线保留1.5mm间隙。腕部装饰独立保留。'
 report[name]={'fabric_vertices':len(mesh.vertices),'fabric_faces':len(mesh.polygons),'hardware_vertices':len(hw.data.vertices),'clearance':dis.strength,'wrist_cutoff':cutoff}
bpy.context.view_layer.update()
(root/'shell_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
for a in bpy.context.screen.areas:a.tag_redraw()
print(json.dumps(report,ensure_ascii=False))
