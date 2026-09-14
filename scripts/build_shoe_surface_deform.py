"""Bind shoes to a deforming foot surface at the existing fitted pose."""
import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils import Matrix
root=Path('D:/project/blender_learning/validation/shoe_fix_20260909')
arm=bpy.data.objects['达妮娅_arm'];body=bpy.data.objects['达妮娅_mesh']
shoes=[bpy.data.objects[n] for n in ['左鞋子_鞋面','右鞋子_鞋面','左鞋子_脚部','右鞋子_脚部']]
def world_coords(o):
    bpy.context.view_layer.update()
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return np.array([ev.matrix_world@v.co for v in ev.data.vertices])
before={o.name:world_coords(o) for o in [body]+shoes}
for n,coords in before.items():np.save(root/(n+'_before.npy'),coords)
pose={p.name:[list(r) for r in p.matrix_basis] for p in arm.pose.bones}
(root/'pose_reference.json').write_text(json.dumps(pose,ensure_ascii=False),encoding='utf8')
original={o.name:dict(world=o.matrix_world.copy(),parent=o.parent,type=o.parent_type,bone=o.parent_bone,inverse=o.matrix_parent_inverse.copy(),basis=o.matrix_basis.copy()) for o in shoes}
active=bpy.context.view_layer.objects.active;selected=list(bpy.context.selected_objects);mode=bpy.context.mode
created=[];added=[]
try:
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    col=bpy.data.collections.new('鞋子变形_辅助');bpy.context.scene.collection.children.link(col)
    targets={}
    for side,sign in [('L',1),('R',-1)]:
        faces=[p for p in body.data.polygons if p.material_index==24 and all(body.data.vertices[i].co.z<.34 and sign*body.data.vertices[i].co.x>0 for i in p.vertices)]
        ids=sorted({i for p in faces for i in p.vertices});mapping={i:j for j,i in enumerate(ids)}
        mesh=bpy.data.meshes.new('FootSurface_'+side)
        mesh.from_pydata([body.data.vertices[i].co.copy() for i in ids],[],[[mapping[i] for i in p.vertices] for p in faces]);mesh.update()
        target=bpy.data.objects.new('鞋子变形参考.'+side,mesh);col.objects.link(target);created.append(target)
        target.matrix_world=body.matrix_world.copy()
        target.parent=arm;target.matrix_world=body.matrix_world.copy()
        for vg in body.vertex_groups:target.vertex_groups.new(name=vg.name)
        for old,new in mapping.items():
            for g in body.data.vertices[old].groups:
                if body.vertex_groups[g.group].name in arm.data.bones:target.vertex_groups[g.group].add([new],g.weight,'REPLACE')
        bm=bmesh.new();bm.from_mesh(mesh)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.000001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.0000001)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bm.to_mesh(mesh);bm.free();mesh.update()
        am=target.modifiers.new('与身体相同的骨骼变形','ARMATURE');am.object=arm
        am.use_deform_preserve_volume=body.modifiers[0].use_deform_preserve_volume
        target.hide_render=True;target.display_type='WIRE'
        target['说明']='从脚部皮肤提取的隐藏变形参考；鞋子表面变形绑定在 2026-09-09 当前姿势。请保留。'
        targets[side]=target
    bpy.context.view_layer.update()
    report={}
    for o in shoes:
        ref=original[o.name]
        # Remove the rigid bone-parent motion before adding surface following.
        o.parent_type='OBJECT';o.parent_bone='';o.matrix_parent_inverse=arm.matrix_world.inverted();o.matrix_world=ref['world']
        mod=o.modifiers.new('鞋子随脚变形_保持当前贴合','SURFACE_DEFORM');mod.target=targets['L' if o.name.startswith('左') else 'R'];mod.falloff=4
        added.append((o,mod))
        bpy.context.view_layer.update()
        with bpy.context.temp_override(object=o,active_object=o):bpy.ops.object.surfacedeform_bind(modifier=mod.name)
        if not mod.is_bound:raise RuntimeError('Bind failed '+o.name)
        error=float(np.max(np.linalg.norm(world_coords(o)-before[o.name],axis=1)))
        report[o.name]={'bound':mod.is_bound,'vertices':len(o.data.vertices),'max_world_displacement':error}
        if error>1e-6:raise RuntimeError('Position changed '+o.name+' '+str(error))
        o['变形说明']='鞋子随脚表面变形；绑定基准为当前已调好的姿势。无需重新绑定或自动权重。'
    for t in targets.values():t.hide_set(True)
    report['body_max_displacement']=float(np.max(np.linalg.norm(world_coords(body)-before[body.name],axis=1)))
    (root/'binding_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False))
except Exception:
    for o,mod in added:o.modifiers.remove(mod)
    for o in shoes:
        r=original[o.name];o.parent=r['parent'];o.parent_type=r['type'];o.parent_bone=r['bone'];o.matrix_parent_inverse=r['inverse'];o.matrix_basis=r['basis']
    for o in created:bpy.data.objects.remove(o,do_unlink=True)
    raise
finally:
    for o in bpy.context.selected_objects:o.select_set(False)
    for o in selected:o.select_set(True)
    bpy.context.view_layer.objects.active=active
    if mode=='POSE':bpy.ops.object.mode_set(mode='POSE')
    bpy.context.view_layer.update()
