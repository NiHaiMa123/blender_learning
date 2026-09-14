"""Phase 10f: fix overexposure, single-leaf framing, twig length, cluster spread."""
import bpy, math, os, sys
from mathutils import Euler, Vector
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR

STUDIO = 'LEAF_STUDIO'

# darker red ramp (linear values -> visible red, not pink)
m = bpy.data.materials['MapleLeaf2']
nt = m.node_tree
ramp = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeValToRGB')
cr = ramp.color_ramp
els = sorted(cr.elements, key=lambda e: e.position)
els[0].position = 0.0;  els[0].color = (0.015, 0.001, 0.0005, 1)
els[1].position = 0.4;  els[1].color = (0.18, 0.008, 0.001, 1)
els[2].position = 0.7;  els[2].color = (0.42, 0.025, 0.002, 1)
els[3].position = 1.0;  els[3].color = (0.65, 0.09, 0.005, 1)
bsdf = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
bsdf.inputs['Emission Strength'].default_value = 0.1

# cut the lights hard
sun = bpy.data.objects.get('StudioSun')
if sun:
    sun.data.energy = 2.0
area = bpy.data.objects.get('StudioArea')
if area:
    area.data.energy = 180
fill = bpy.data.objects.get('StudioFill')
if fill:
    fill.data.energy = 60

# twig: short stick ending just below convergence
TIP = Vector((0.9, 0.0, 0.12))
twig = bpy.data.objects.get('ClusterTwig')
if twig:
    twig.scale = (0.7, 0.7, 0.45)          # depth 0.35 -> ~0.16
    twig.location = TIP - Vector((0, 0, 0.06))
    twig.hide_render = True

# cluster: wider fan, slight scale variance, staggered depth
import random
random.seed(7)
half_h = 0.125
for i in range(7):
    c = bpy.data.objects.get(f'Clu_{i}')
    if not c:
        continue
    a = math.radians(-85 + 28 * i)
    tier = -0.025 * (i % 3)
    tilt = math.radians(-35 + 9 * i)
    sc = 0.9 + 0.25 * random.random()
    c.scale = (sc, sc, sc)
    c.rotation_euler = Euler((tilt, math.radians(8 * (i - 3)), a), 'XYZ')
    R = c.rotation_euler.to_matrix()
    off = R @ Vector((0, 0, -half_h * sc))
    c.location = TIP + Vector((0, -0.015 * i, tier)) - off
    c.hide_render = True

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100

# lineup
for i in range(3):
    o = bpy.data.objects[f'LeafCard_{i}']
    o.hide_render = False
    o.location = (i * 0.35 - 0.35, 0, 0)
    o.rotation_euler = (0, 0, 0)
cam.data.lens = 45
cam.location = (0, -1.4, 0)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p10f_lineup.png')
bpy.ops.render.render(write_still=True)

# single closeup - leaf back to origin!
for i in (1, 2):
    bpy.data.objects[f'LeafCard_{i}'].hide_render = True
leaf0 = bpy.data.objects['LeafCard_0']
leaf0.location = (0, 0, 0)
cam.data.lens = 55
cam.location = (0, -0.85, 0.02)
s.render.filepath = os.path.join(RENDER_DIR, 'p10f_single.png')
bpy.ops.render.render(write_still=True)

# cluster
leaf0.hide_render = True
for i in range(7):
    bpy.data.objects[f'Clu_{i}'].hide_render = False
if twig:
    twig.hide_render = False
cam.data.lens = 50
cam.location = (0.9, -1.15, 0.12)
s.render.filepath = os.path.join(RENDER_DIR, 'p10f_cluster.png')
bpy.ops.render.render(write_still=True)

save()
print('P10F DONE')
