import bpy,json
from mathutils import Matrix
body=bpy.data.objects['达妮娅_mesh'];arm=bpy.data.objects['达妮娅_arm']
for s,n in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[n];o.modifiers['指尖包覆余量'].strength=.0016
 fs=[p for p in body.data.polygons if p.material_index==25 and all(body.data.vertices[i].co.x*(1 if s=='L' else -1)>.30 and .85<body.data.vertices[i].co.z<1.17 for i in p.vertices)]
 ids=sorted({i for p in fs for i in p.vertices});mapping={i:j for j,i in enumerate(ids)}
 mesh=bpy.data.meshes.new('GloveNails_'+s);mesh.from_pydata([body.data.vertices[i].co.copy() for i in ids],[],[[mapping[i] for i in p.vertices] for p in fs]);mesh.update()
 ref=bpy.data.objects.new('手套指甲包覆参考.'+s,mesh);bpy.data.objects['手套变形参考.'+s].users_collection[0].objects.link(ref);ref.parent=arm;ref.matrix_world=Matrix.Identity(4)
 for vg in body.vertex_groups:ref.vertex_groups.new(name=vg.name)
 for old,new in mapping.items():
  for g in body.data.vertices[old].groups:
   if body.vertex_groups[g.group].name in arm.data.bones:ref.vertex_groups[g.group].add([new],g.weight,'REPLACE')
 am=ref.modifiers.new('与素体指甲同步','ARMATURE');am.object=arm;ref.hide_render=True;ref.hide_set(True)
 cap={i for p in o.data.polygons if p.index>=5903 for i in p.vertices};vg=o.vertex_groups.new(name='指甲覆盖区域')
 vg.add(list(cap),1,'REPLACE')
 for e in o.data.edges:
  a,b=e.vertices
  if a in cap and b not in cap:vg.add([b],.5,'REPLACE')
  if b in cap and a not in cap:vg.add([a],.5,'REPLACE')
 sub=o.modifiers.new('指尖贴合精度','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=1;sub.render_levels=1;o.modifiers.move(len(o.modifiers)-1,0)
 sw=o.modifiers.new('指甲包覆防穿','SHRINKWRAP');sw.target=ref;sw.wrap_method='NEAREST_SURFACEPOINT';sw.wrap_mode='OUTSIDE';sw.offset=.001;sw.vertex_group=vg.name
 # Before Solidify, after armature and normal displacement.
 idx=list(o.modifiers).index(o.modifiers['手套边缘厚度']);o.modifiers.move(len(o.modifiers)-1,idx)
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:a.tag_redraw()
print('Local nail covers added; hand and nails remain unchanged.')
