"""Phase 10j: kill specular blowout on edge-on leaf, final cluster render."""
import bpy, math, os, sys
from mathutils import Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import save, RENDER_DIR

m = bpy.data.materials['MapleLeaf2']
bsdf = next(n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
if bsdf.inputs.get('Specular IOR Level'):
    bsdf.inputs['Specular IOR Level'].default_value = 0.15
if bsdf.inputs.get('Roughness'):
    bsdf.inputs['Roughness'].default_value = 0.7   # rough leaves, no sheen

rim = bpy.data.objects.get('StudioRim')
if rim:
    rim.data.energy = 55

# nudge the edge-on leaf (top pair, right side ~az 285) more face-on
for i in range(7):
    c = bpy.data.objects.get(f'Clu_{i}')
    if c:
        c.rotation_euler.rotate_axis('Y', math.radians(-12))

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100
cam.data.lens = 42
cam.location = (0.9, -1.25, 0.1)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p10j_cluster.png')
bpy.ops.render.render(write_still=True)
save()
print('P10J DONE')
