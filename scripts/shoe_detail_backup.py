import bpy,json,collections,sys,inspect
from pathlib import Path
root=Path('D:/project/blender_learning/validation/shoe_fix_20260909');root.mkdir(exist_ok=True)
shoes=[o for o in bpy.context.scene.objects if '鞋' in o.name and o.visible_get()]
def summarize(o):
    coords=[o.matrix_world@v.co for v in o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    weights=collections.Counter()
    for v in o.data.vertices:
        for g in v.groups:
            if g.weight>0.001:weights[o.vertex_groups[g.group].name]+=1
    return dict(name=o.name,n=len(o.data.vertices),parent=o.parent.name if o.parent else None,parent_type=o.parent_type,parent_bone=o.parent_bone,world=[list(r) for r in o.matrix_world],bounds=[[min(v[i] for v in coords) for i in range(3)],[max(v[i] for v in coords) for i in range(3)]],weights=weights,constraints=[(c.name,c.type) for c in o.constraints])
print(json.dumps([summarize(o) for o in shoes],ensure_ascii=False))
for name,mod in list(sys.modules.items()):
    if 'blender_mcp' in name:
        for _,cls in inspect.getmembers(mod,inspect.isclass):
            if hasattr(cls,'get_viewport_screenshot'):
                print(inspect.getsource(cls.get_viewport_screenshot))
backup=root/'before_shoe_deform.blend'
if not backup.exists():
    bpy.ops.wm.save_as_mainfile(filepath=str(backup),copy=True)
print('BACKUP',str(backup))
