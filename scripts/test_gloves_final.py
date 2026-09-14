import bpy,json,math,numpy as np,time
from pathlib import Path
from mathutils import Quaternion
from mathutils.bvhtree import BVHTree
root=Path('D:/project/blender_learning/validation/glove_fix_20260909');arm=bpy.data.objects['达妮娅_arm'];body=bpy.data.objects['达妮娅_mesh']
names=['右手套','左手套','右手套_腕部装饰','左手套_腕部装饰']
shoes=[o for o in bpy.context.scene.objects if o.type=='MESH' and '鞋子_' in o.name and o.visible_get()]
original={p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.rotation_euler.copy(),p.rotation_axis_angle[:],p.scale.copy()) for p in arm.pose.bones}
bpy.app.driver_namespace['glove_verified_pose_channels']=original
def restore():
 for n,(loc,q,e,a,sc) in original.items():
  p=arm.pose.bones[n];p.location=loc;p.rotation_quaternion=q;p.rotation_euler=e;p.rotation_axis_angle=a;p.scale=sc
 bpy.context.view_layer.update()
def mesh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices],[list(p.vertices) for p in e.data.polygons]
bpy.context.view_layer.update();base={n:np.array(mesh(bpy.data.objects[n])[0]) for n in names};shoebase={o.name:np.array(mesh(o)[0]) for o in shoes}
def measure(label):
 t=time.perf_counter();bpy.context.view_layer.update();bv,bf=mesh(body);bt=BVHTree.FromPolygons(bv,bf);out={'pose':label,'objects':{}}
 for n in names:
  o=bpy.data.objects[n];v,f=mesh(o);motion=float(np.max(np.linalg.norm(np.array(v)-base[n],axis=1)))
  out['objects'][n]={'visible_body_crossing_pairs':len(bt.overlap(BVHTree.FromPolygons(v,f))),'max_motion':motion,'finite':bool(np.isfinite(np.array(v)).all())}
 out['seconds']=time.perf_counter()-t;return out
def rotate(n,axis,degrees):
 p=arm.pose.bones[n];p.rotation_quaternion=original[n][1]@Quaternion(axis,math.radians(degrees))
report=[]
try:
 report.append(measure('original_fitted_pose'))
 for axis,deg in [((1,0,0),-35),((1,0,0),35),((0,0,1),-25),((0,0,1),25)]:
  restore()
  for s in ['L','R']:rotate('手首.'+s,axis,deg)
  report.append(measure('wrist_'+str(axis)+'_'+str(deg)))
 for label,angles in [('half_curl',(25,35,20)),('full_curl',(50,65,35))]:
  restore()
  for s in ['L','R']:
   for finger in ['人指','中指','薬指','小指']:
    for joint,deg in zip(['１','２','３'],angles):rotate(finger+joint+'.'+s,(1,0,0),deg)
   rotate('親指１.'+s,(1,0,0),20);rotate('親指２.'+s,(1,0,0),25)
  report.append(measure(label))
 restore()
 for s in ['L','R']:
  rotate('人指１.'+s,(1,0,0),55);rotate('人指２.'+s,(1,0,0),65);rotate('人指３.'+s,(1,0,0),35)
 report.append(measure('index_independent_curl'))
finally:restore()
report.append({'restored_glove_max_error':{n:float(np.max(np.linalg.norm(np.array(mesh(bpy.data.objects[n])[0])-base[n],axis=1))) for n in names},'shoes_max_error':{o.name:float(np.max(np.linalg.norm(np.array(mesh(o)[0])-shoebase[o.name],axis=1))) for o in shoes}})
# Toggle off restores the complete original hand mesh as well as hiding the gloves.
mask=body.modifiers['穿戴手套_隐藏内部手部'];mask.show_viewport=False;bpy.context.view_layer.update();bv=np.array(mesh(body)[0]);prior=np.load(root/'body_before.npy')
toggle_error=float(np.max(np.linalg.norm(bv-prior,axis=1))) if bv.shape==prior.shape else None
report.append({'mask_disabled_original_body_error':toggle_error})
mask.show_viewport=True;bpy.context.view_layer.update()
(root/'final_motion_tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
