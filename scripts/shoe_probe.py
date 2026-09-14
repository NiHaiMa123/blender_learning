import bpy,json,sys,inspect,collections
o=bpy.data.objects['达妮娅_mesh'];a=bpy.data.objects['达妮娅_arm']
print('MODULES',[(n,getattr(m,'__file__','')) for n,m in sys.modules.items() if 'mcp' in n.lower()])
print('BODY',list(o.matrix_world), 'DQ',o.modifiers[0].use_deform_preserve_volume)
print('LOW_WEIGHTS',collections.Counter(o.vertex_groups[g.group].name for v in o.data.vertices if (o.matrix_world@v.co).z<.27 for g in v.groups if g.weight>.001))
print('POSE_ACTIVE',getattr(bpy.context.active_pose_bone,'name',None))
print('VIEW',[(ar.type,ar.width,ar.height) for ar in bpy.context.screen.areas])
print('OPS', [k.identifier for k in bpy.ops.object.surfacedeform_bind.get_rna_type().properties])
for n,m in list(sys.modules.items()):
 if 'mcp' in n.lower():
  for _,c in inspect.getmembers(m,inspect.isclass):
   if hasattr(c,'get_viewport_screenshot'):print(inspect.getsource(c.get_viewport_screenshot))
