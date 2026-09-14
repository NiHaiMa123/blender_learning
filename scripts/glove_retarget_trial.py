import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/project/blender_learning/validation/glove_fix_20260909')
source=bpy.data.objects['达妮娅_红色毛茸袖形态_arm'];target=bpy.data.objects['达妮娅_arm'];body=bpy.data.objects['达妮娅_mesh']
def world(o):
 bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return np.array([ev.matrix_world@v.co for v in ev.data.vertices])
if not (root/'body_before.npy').exists():np.save(root/'body_before.npy',world(body))
report={}
for s,name in [('R','右手套'),('L','左手套')]:
 o=bpy.data.objects[name];template=bpy.data.objects[name+'.001']
 if not (root/(name+'_original_world.npy')).exists():np.save(root/(name+'_original_world.npy'),world(o))
 if 'glove_original_mesh_'+s not in bpy.app.driver_namespace:bpy.app.driver_namespace['glove_original_mesh_'+s]=o.data.copy()
 # Source templates have a display offset at object level. Their mesh coordinates
 # and bone rest coordinates share the imported armature space.
 names=['ひじ','手捩','手首','親指０','親指１','親指２']+[f+d for f in ['人指','中指','薬指','小指'] for d in ['１','２','３']]
 src=[];dst=[]
 for n in names:
  a=source.data.bones.get(n+'.'+s);b=target.pose.bones.get(n+'.'+s)
  if a and b:src.append(list(a.head_local));dst.append(list(b.head))
 for n in ['親指２','人指３','中指３','薬指３','小指３']:
  src.append(list(source.data.bones[n+'.'+s].tail_local));dst.append(list(target.pose.bones[n+'.'+s].tail))
 src=np.array(src);dst=np.array(dst)
 # 3D polyharmonic interpolation with affine term; landmarks are bone joints.
 n=len(src);d=np.linalg.norm(src[:,None,:]-src[None,:,:],axis=2);P=np.c_[np.ones(n),src]
 A=np.block([[d+np.eye(n)*1e-8,P],[P.T,np.zeros((4,4))]])
 coeff=np.linalg.solve(A,np.r_[dst,np.zeros((4,3))])
 raw=np.array([v.co for v in template.data.vertices])
 out=np.c_[np.linalg.norm(raw[:,None,:]-src[None,:,:],axis=2),np.ones(len(raw)),raw]@coeff
 for mod in o.modifiers:
  if mod.type=='SURFACE_DEFORM':mod.show_viewport=False;mod.show_render=False
 inv=o.matrix_world.inverted();new=[inv@Vector(v) for v in out]
 old=[v.co.copy() for v in o.data.vertices]
 delta=[n-p for n,p in zip(new,old)]
 if o.data.shape_keys:
  for k in o.data.shape_keys.key_blocks:
   for v,dv in zip(k.data,delta):v.co+=dv
 for v,p in zip(o.data.vertices,new):v.co=p
 o.data.update()
 np.save(root/(name+'_retarget_world.npy'),out)
 report[name]={'landmarks':n,'joint_fit_error':float(np.max(np.linalg.norm((A@coeff)[:n]-dst,axis=1))),'raw_template_difference':float(np.max(np.linalg.norm(raw-np.array([v.co for v in bpy.app.driver_namespace['glove_original_mesh_'+s].vertices]),axis=1)))}
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:a.tag_redraw()
print(json.dumps(report,ensure_ascii=False))
