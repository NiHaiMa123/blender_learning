"""Phase 10e: deepen maple red, fix twig/stem connection, fuller cluster."""
import bpy, math, os, sys
from mathutils import Euler, Vector
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR

STUDIO = 'LEAF_STUDIO'

# deeper maple red ramp
m = bpy.data.materials['MapleLeaf2']
nt = m.node_tree
ramp = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeValToRGB')
cr = ramp.color_ramp
els = sorted(cr.elements, key=lambda e: e.position)
els[0].color = (0.03, 0.002, 0.001, 1)      # shadow: near-black red
els[1].color = (0.30, 0.012, 0.002, 1)      # deep red
els[2].color = (0.62, 0.05, 0.004, 1)       # maple red
els[3].color = (0.90, 0.20, 0.015, 1)       # orange-red bright
bsdf = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
bsdf.inputs['Emission Strength'].default_value = 0.15

# twig: raise so top overlaps the stem convergence point
twig = bpy.data.objects.get('ClusterTwig')
TIP = Vector((0.9, 0.0, 0.12))
if twig:
    twig.scale = (0.8, 0.8, 0.8)
    twig.location = TIP - Vector((0, 0, 0.14))
    twig.hide_render = True

# fuller cluster: 7 leaves, bigger, staggered tiers
half_h = 0.125
for i in range(7):
    c = bpy.data.objects.get(f'Clu_{i}')
    if not c:
        src = bpy.data.objects[f'LeafCard_{i % 3}']
        c = src.copy(); c.data = src.data; c.name = f'Clu_{i}'
        col(STUDIO).objects.link(c)
    a = math.radians(-78 + 26 * i)
    tier = -0.03 * (i % 3)
    tilt = math.radians(-30 + 10 * i)
    c.scale = (1.15, 1.15, 1.15)
    c.rotation_euler = Euler((tilt, math.radians(6 * (i - 3)), a), 'XYZ')
    R = c.rotation_euler.to_matrix()
    off = R @ Vector((0, 0, -half_h * 1.15))
    c.location = TIP + Vector((0, 0, tier)) - off
    c.hide_render = True

# backdrop further back & tilted to kill horizon band
bp = bpy.data.objects.get('StudioBackdrop')
if bp:
    bp.location = (0.4, 5.0, 0.5)
    bp.rotation_euler = Euler((math.radians(75), 0, 0), 'XYZ')
    bp.scale = (8, 8, 8)

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
s.render.filepath = os.path.join(RENDER_DIR, 'p10e_lineup.png')
bpy.ops.render.render(write_still=True)

# single
for i in (1, 2):
    bpy.data.objects[f'LeafCard_{i}'].hide_render = True
cam.data.lens = 70
cam.location = (0, -0.8, 0.02)
s.render.filepath = os.path.join(RENDER_DIR, 'p10e_single.png')
bpy.ops.render.render(write_still=True)

# cluster
bpy.data.objects['LeafCard_0'].hide_render = True
for i in range(7):
    bpy.data.objects[f'Clu_{i}'].hide_render = False
if twig:
    twig.hide_render = False
cam.data.lens = 50
cam.location = (0.9, -1.2, 0.1)
s.render.filepath = os.path.join(RENDER_DIR, 'p10e_cluster.png')
bpy.ops.render.render(write_still=True)

save()
print('P10E DONE')
