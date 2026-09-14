import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Quaternion,Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/project/blender_learning/validation/shoe_fix_20260909')
arm=bpy.data.objects['达妮娅_arm'];body=bpy.data.objects['达妮娅_mesh'];shoe=bpy.data.objects['右鞋子_鞋面'];mod=shoe.modifiers['鞋子随脚变形_保持当前贴合']
p=arm.pose.bones['足首D.R'];orig=p.rotation_quaternion.copy()
def coords(o):
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
bf=[list(f.vertices) for f in body.data.polygons if f.material_index==24 and all(body.data.vertices[i].co.z<.34 and body.data.vertices[i].co.x<0 for i in f.vertices)]
sf=[list(f.vertices) for f in shoe.data.polygons]
def bind(falloff):
 p.rotation_quaternion=orig;bpy.context.view_layer.update()
 with bpy.context.temp_override(object=shoe,active_object=shoe):
  if mod.is_bound:bpy.ops.object.surfacedeform_bind(modifier=mod.name)
  mod.falloff=falloff;bpy.ops.object.surfacedeform_bind(modifier=mod.name)
 assert mod.is_bound
def crossing():
 return len(BVHTree.FromPolygons(coords(body),bf).overlap(BVHTree.FromPolygons(coords(shoe),sf)))
active=bpy.context.object;mode=active.mode
bpy.ops.object.mode_set(mode='OBJECT')
report=[]
try:
 for falloff in [4,8,16]:
  bind(falloff);counts=[crossing()]
  for axis,deg in [('X',-25),('X',25),('Y',-15),('Y',15),('Z',-15),('Z',15)]:
   p.rotation_quaternion=orig@Quaternion(Vector((axis=='X',axis=='Y',axis=='Z')),math.radians(deg));counts.append(crossing())
  report.append({'falloff':falloff,'crossings':counts})
 best=min(report,key=lambda r:(max(r['crossings']),sum(r['crossings']),r['falloff']))
 bind(best['falloff'])
finally:
 p.rotation_quaternion=orig;bpy.context.view_layer.objects.active=active;bpy.ops.object.mode_set(mode=mode);bpy.context.view_layer.update()
error=float(np.max(np.linalg.norm(np.array(coords(shoe))-np.load(root/(shoe.name+'_before.npy')),axis=1)))
assert error<1e-6
(root/'cuff_refinement.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({'tests':report,'chosen':best,'baseline_error':error}))
