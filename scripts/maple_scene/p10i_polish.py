"""Phase 10i: tame rim light (white-hot backleaf), tighten node spacing."""
import bpy, math, os, sys, random
from mathutils import Euler, Vector
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import save, RENDER_DIR

rim = bpy.data.objects.get('StudioRim')
if rim:
    rim.data.energy = 90
sun = bpy.data.objects.get('StudioSun')
if sun:
    sun.data.energy = 2.2

# tighten: nodes closer together, leaves a touch smaller
random.seed(11)
half_h = 0.125
base = Vector((0.9, 0.02, -0.10))
lean = Euler((math.radians(8), 0, math.radians(-6)), 'XYZ')
up_dir = lean.to_matrix() @ Vector((0, 0, 1))
twig_len = 0.34
plan = []
nodes_t = [0.40, 0.62, 0.80]
az0 = 15
for ni, t in enumerate(nodes_t):
    node_az = az0 + 90 * ni
    for side in (0, 180):
        plan.append((t, node_az + side + random.uniform(-8, 8),
                     30 + random.uniform(-6, 8), 0.75 + 0.2 * random.random()))
plan.append((0.95, az0 + 45, 8, 0.7))

for i, (t, az, tilt, sc) in enumerate(plan):
    c = bpy.data.objects.get(f'Clu_{i}')
    if not c:
        continue
    node_pos = base + up_dir * (t * twig_len)
    c.scale = (sc, sc, sc)
    c.rotation_euler = Euler((math.radians(tilt), 0, math.radians(az)), 'XYZ')
    R = c.rotation_euler.to_matrix()
    off = R @ Vector((0, 0, -half_h * sc))
    c.location = Vector(node_pos) - off
    c.hide_render = False

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100
for i in range(3):
    bpy.data.objects[f'LeafCard_{i}'].hide_render = True
bpy.data.objects['ClusterTwig'].hide_render = False
cam.data.lens = 42
cam.location = (0.9, -1.25, 0.1)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p10i_cluster.png')
bpy.ops.render.render(write_still=True)
save()
print('P10I DONE')
