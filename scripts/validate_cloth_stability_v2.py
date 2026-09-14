import bpy
import json
from mathutils import Vector

scene = bpy.context.scene
obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = obj.modifiers['CLOTH_REBUILD_SKIRT']
depsgraph = bpy.context.evaluated_depsgraph_get()

def sample(frame):
    scene.frame_set(frame)
    depsgraph.update()
    ev = obj.evaluated_get(depsgraph)
    coords = [v.co for v in ev.data.vertices]
    center = sum(coords, Vector()) / len(coords)
    mins = [min(v[i] for v in coords) for i in range(3)]
    maxs = [max(v[i] for v in coords) for i in range(3)]
    return {'frame': frame, 'center': [round(float(x), 5) for x in center], 'min': [round(float(x), 5) for x in mins], 'max': [round(float(x), 5) for x in maxs]}

render = scene.render
saved = (render.engine, render.resolution_percentage, render.filepath)
cycles = scene.cycles if hasattr(scene, 'cycles') else None
saved_samples = cycles.samples if cycles and render.engine == 'CYCLES' else None
render.resolution_percentage = 50
if saved_samples is not None:
    cycles.samples = 16
for frame, tag in [(1, 'f001'), (40, 'f040')]:
    scene.frame_set(frame)
    render.filepath = r'D:\project\blender_learning\renders\cloth_rebuild_stable_%s.png' % tag
    bpy.ops.render.render(write_still=True)
render.engine, render.resolution_percentage, render.filepath = saved
if saved_samples is not None:
    cycles.samples = saved_samples
scene.frame_set(40)
result = {'baked': bool(mod.point_cache.is_baked), 'samples': [sample(1), sample(20), sample(40)], 'renders': ['cloth_rebuild_stable_f001.png', 'cloth_rebuild_stable_f040.png']}
bpy.ops.wm.save_as_mainfile(filepath=r'D:\software\blender\project\今汐_cloth_rebuild_stable_preview_v2.blend', check_existing=False)
print(json.dumps(result, ensure_ascii=False, indent=2))
