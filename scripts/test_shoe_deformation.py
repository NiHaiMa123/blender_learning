import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Quaternion,Vector
from mathutils.bvhtree import BVHTree
root=Path('D:/project/blender_learning/validation/shoe_fix_20260909')
arm=bpy.data.objects['达妮娅_arm'];body=bpy.data.objects['达妮娅_mesh']
shoes=[bpy.data.objects[n] for n in ['左鞋子_鞋面','右鞋子_鞋面','左鞋子_脚部','右鞋子_脚部']]
def coords(o):
    bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [e.matrix_world@v.co for v in e.data.vertices]
def tree(v,f):return BVHTree.FromPolygons(v,f,all_triangles=False,epsilon=0)
baseline={o.name:coords(o) for o in [body]+shoes}
bonebase={s:arm.pose.bones['足首D.'+s].matrix.copy() for s in ['L','R']}
original={p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.rotation_euler.copy(),p.rotation_axis_angle[:],p.scale.copy()) for p in arm.pose.bones}
faces={s:[list(p.vertices) for p in body.data.polygons if p.material_index==24 and all(body.data.vertices[i].co.z<.34 and body.data.vertices[i].co.x*(1 if s=='L' else -1)>0 for i in p.vertices)] for s in ['L','R']}
sf={o.name:[list(p.vertices) for p in o.data.polygons] for o in shoes}
def restore():
    for n,(loc,quat,euler,axis,scale) in original.items():
        p=arm.pose.bones[n];p.location=loc;p.rotation_quaternion=quat;p.rotation_euler=euler;p.rotation_axis_angle=axis;p.scale=scale
    bpy.context.view_layer.update()
def measure(label):
    bc=coords(body);bvh={s:tree(bc,faces[s]) for s in ['L','R']};out={'pose':label,'shoes':{}}
    for o in shoes:
        side='L' if o.name.startswith('左') else 'R';vc=coords(o)
        d=arm.matrix_world@arm.pose.bones['足首D.'+side].matrix@bonebase[side].inverted()@arm.matrix_world.inverted()
        old=[d@v for v in baseline[o.name]]
        out['shoes'][o.name]={'surface_crossings':len(bvh[side].overlap(tree(vc,sf[o.name]))),'old_rigid_crossings':len(bvh[side].overlap(tree(old,sf[o.name]))),'max_motion':float(np.max(np.linalg.norm(np.array(vc)-np.array(baseline[o.name]),axis=1)))}
    return out
report=[]
try:
    report.append(measure('baseline'))
    for prefix,axis,degrees in [('足首D.','X',-25),('足首D.','X',25),('足首D.','Y',-15),('足首D.','Y',15),('足首D.','Z',-15),('足首D.','Z',15),('足先EX.','X',-15),('足先EX.','X',15)]:
        restore()
        for s in ['L','R']:
            p=arm.pose.bones[prefix+s];p.rotation_quaternion=original[p.name][1]@Quaternion(Vector((axis=='X',axis=='Y',axis=='Z')),math.radians(degrees))
        bpy.context.view_layer.update();report.append(measure(prefix+axis+str(degrees)))
finally:restore()
report.append({'restored_max_error':{o.name:float(np.max(np.linalg.norm(np.array(coords(o))-np.load(root/(o.name+'_before.npy')),axis=1))) for o in [body]+shoes}})
(root/'rotation_test.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
