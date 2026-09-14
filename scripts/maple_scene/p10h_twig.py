"""Phase 10h: correct maple cluster = OPPOSITE phyllotaxis along a twig.
3 nodes x leaf pair (decussate 90deg between nodes) + 1 terminal leaf."""
import bpy, math, os, sys, random
from mathutils import Euler, Vector
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR

STUDIO = 'LEAF_STUDIO'
random.seed(11)
half_h = 0.125

# twig: angled slightly, ~34cm, thin
twig = bpy.data.objects.get('ClusterTwig')
twig_len = 0.34
if twig:
    twig.scale = (0.55, 0.55, twig_len / 0.35)
    twig.rotation_euler = Euler((math.radians(8), 0, math.radians(-6)), 'XYZ')
else:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=twig_len)
    twig = bpy.context.object
    twig.name = 'ClusterTwig'
    move = col(STUDIO)
    for uc in list(twig.users_collection):
        uc.objects.unlink(twig)
    move.objects.link(twig)
twig.location = (0.9, 0, 0)
twig.hide_render = True

# twig base point (world, lower end) — leaves attach along it
base = Vector((0.9, 0.02, -0.13))
lean = Euler((math.radians(8), 0, math.radians(-6)), 'XYZ')
up_dir = lean.to_matrix() @ Vector((0, 0, 1))

def place_leaf(c, node_pos, azimuth_deg, tilt_deg, scale):
    """leaf local +Z (blade dir) tilted outward by tilt_deg, spun azimuth;
    stem tip (local -Z bottom) lands on node_pos"""
    c.scale = (scale, scale, scale)
    c.rotation_euler = Euler((math.radians(tilt_deg), 0, math.radians(azimuth_deg)), 'XYZ')
    R = c.rotation_euler.to_matrix()
    off = R @ Vector((0, 0, -half_h * scale))
    c.location = Vector(node_pos) - off

plan = []                     # (t along twig 0..1, azimuth, tilt, scale)
nodes_t = [0.30, 0.58, 0.82]
az0 = 15
for ni, t in enumerate(nodes_t):
    node_az = az0 + 90 * ni   # decussate: rotate pair 90deg each node
    for side in (0, 180):
        plan.append((t, node_az + side + random.uniform(-8, 8),
                     32 + random.uniform(-6, 8), 0.85 + 0.25 * random.random()))
plan.append((0.97, az0 + 45, 8, 0.8))   # terminal leaf, nearly upright

for i in range(len(plan)):
    c = bpy.data.objects.get(f'Clu_{i}')
    if not c:
        src = bpy.data.objects[f'LeafCard_{i % 3}']
        c = src.copy(); c.data = src.data; c.name = f'Clu_{i}'
        col(STUDIO).objects.link(c)
    t, az, tilt, sc = plan[i]
    node_pos = base + up_dir * (t * twig_len)
    place_leaf(c, node_pos, az, tilt, sc)
    c.hide_render = False

# hide leftover higher-index cluster objs if any
for i in range(len(plan), 10):
    o = bpy.data.objects.get(f'Clu_{i}')
    if o:
        o.hide_render = True

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100

for i in range(3):
    bpy.data.objects[f'LeafCard_{i}'].hide_render = True
twig.hide_render = False
cam.data.lens = 42
cam.location = (0.9, -1.25, 0.1)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p10h_cluster.png')
bpy.ops.render.render(write_still=True)

save()
print('P10H DONE')
