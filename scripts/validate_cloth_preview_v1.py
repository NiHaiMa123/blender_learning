import bpy
import json
from mathutils import Vector

scene = bpy.context.scene
cloth_obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
mod = cloth_obj.modifiers['CLOTH_REBUILD_SKIRT']
depsgraph = bpy.context.evaluated_depsgraph_get()

def sample_frame(frame):
    scene.frame_set(frame)
    depsgraph.update()
    evaluated = cloth_obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    verts = mesh.vertices
    center = sum((v.co for v in verts), Vector()) / len(verts)
    coords = [v.co for v in verts]
    mins = [min(v[i] for v in coords) for i in range(3)]
    maxs = [max(v[i] for v in coords) for i in range(3)]
    result = {
        'frame': frame,
        'center': [round(float(x), 6) for x in center],
        'min': [round(float(x), 6) for x in mins],
        'max': [round(float(x), 6) for x in maxs],
        'v0': [round(float(x), 6) for x in verts[0].co],
        'vlast': [round(float(x), 6) for x in verts[-1].co],
    }
    evaluated.to_mesh_clear()
    return result

samples = [sample_frame(f) for f in [1, 20, 40, 60, 80]]
render = scene.render
saved = (render.engine, render.resolution_percentage, render.filepath)
cycles = scene.cycles if hasattr(scene, 'cycles') else None
saved_samples = cycles.samples if cycles and render.engine == 'CYCLES' else None
render.resolution_percentage = 50
if saved_samples is not None:
    cycles.samples = 16
for frame, tag in [(1, 'f001'), (80, 'f080')]:
    scene.frame_set(frame)
    render.filepath = r'D:\project\blender_learning\renders\cloth_rebuild_v2_%s.png' % tag
    bpy.ops.render.render(write_still=True)
render.engine, render.resolution_percentage, render.filepath = saved
if saved_samples is not None:
    cycles.samples = saved_samples
scene.frame_set(80)
bpy.ops.wm.save_as_mainfile()
print(json.dumps({'cache_baked': bool(mod.point_cache.is_baked), 'samples': samples, 'renders': ['cloth_rebuild_v2_f001.png', 'cloth_rebuild_v2_f080.png']}, ensure_ascii=False, indent=2))
