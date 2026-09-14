"""Phase 11d: moss -> larger organic patches, less coverage; sink root caps."""
import bpy, math, os, sys
from mathutils import Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import save, RENDER_DIR

m = bpy.data.materials['Bark']
nt = m.node_tree
# moss noise -> larger blobs
mn = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexNoise' and n.inputs['Scale'].default_value < 10]
if mn:
    mn[0].inputs['Scale'].default_value = 1.1
    mn[0].inputs['Detail'].default_value = 2.5
# stricter gate: only strong patches
mr2s = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange']
for n in mr2s:
    if abs(n.inputs['From Min'].default_value - 0.45) < 0.01:
        n.inputs['From Min'].default_value = 0.58
        n.inputs['From Max'].default_value = 0.80
mix = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMix')
mix.inputs['B'].default_value = (0.085, 0.075, 0.012, 1)   # dimmer olive-moss

# sink roots' caps below grade + hide the plaid cap artifact
tr = bpy.data.objects.get('MapleTree')
if tr:
    tr.location.z = -0.35

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1400
s.render.resolution_percentage = 100

cam.data.lens = 50
cam.location = (-4.7, -5.2, 2.6)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p11d_mid.png')
bpy.ops.render.render(write_still=True)

cam.location = (-4.7, -3.0, 0.9)
cam.data.lens = 40
s.render.filepath = os.path.join(RENDER_DIR, 'p11d_base.png')
bpy.ops.render.render(write_still=True)

save()
print('P11D DONE')
