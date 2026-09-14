"""Phase 12: repose skeleton to match reference — thick bole, pronounced S,
big right-sweeping limb. Bare tree (no leaves) for pose check renders."""
import bpy, math, sys, random
from mathutils import Vector, Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR
import os
random.seed(11)

for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    if lc.name in ('TREE', 'LEAF_STUDIO'):
        lc.exclude = False

# clean tree
for o in list(bpy.data.collections.get('TREE').objects):
    bpy.data.objects.remove(o, do_unlink=True)
old = bpy.data.objects.get('MapleTree')
if old:
    bpy.data.objects.remove(old, do_unlink=True)

deep_star = bpy.data.objects['StarDeep']
soft_star = bpy.data.objects['StarSoft']
bark = bpy.data.materials['Bark']
tree_col = col('TREE')

def limb(name, pts, profile, twist_total=0.0):
    cu = bpy.data.curves.new(name + '_cu', 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 10
    cu.bevel_mode = 'OBJECT'
    cu.bevel_object = profile
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    n = len(pts)
    for i, (bp, (co, r)) in enumerate(zip(sp.bezier_points, pts)):
        bp.co = co
        bp.radius = r * (1 + random.uniform(-0.04, 0.04))
        bp.tilt = twist_total * i / (n - 1)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    tree_col.objects.link(o)
    o.data.materials.append(bark)
    return o

# ---------- THICK S-trunk: base -> lean LEFT -> curl RIGHT -> fork ----------
limb('trunk', [
    ((-4.55, 0.00, -0.6), 1.05),
    ((-4.85, 0.00, 0.7), 0.97),
    ((-5.55, 0.05, 1.9), 0.88),
    ((-5.75, 0.10, 3.1), 0.80),
    ((-5.35, 0.12, 4.2), 0.70),
    ((-4.45, 0.10, 5.1), 0.58),
    ((-3.65, 0.05, 5.8), 0.44),
], deep_star, twist_total=math.radians(320))

# roots: thicker flare radiating from fat base
for i, ang in enumerate((-0.7, 0.4, 2.5, 3.7)):
    dx, dy = math.cos(ang) * 1.45, math.sin(ang) * 1.15
    limb(f'root{i}', [
        ((-4.72, 0.0, 0.6), 0.42),
        ((-4.72 + dx * 0.5, dy * 0.5, 0.12), 0.24),
        ((-4.72 + dx, dy, -0.35), 0.07),
    ], deep_star, twist_total=math.radians(100))

# ---------- limbs per reference ----------
# A: up-left, exits top-left of frame
limb('limbA', [
    ((-3.90, 0.05, 5.55), 0.36),
    ((-4.65, 0.15, 6.4), 0.22),
    ((-5.50, 0.30, 7.3), 0.15),
    ((-6.40, 0.40, 8.2), 0.09),
    ((-7.30, 0.45, 9.0), 0.04),
], soft_star, twist_total=math.radians(150))
# B: THE big right sweep across the top
limb('limbB', [
    ((-3.70, 0.00, 5.55), 0.40),
    ((-2.40, 0.10, 6.15), 0.24),
    ((-0.80, 0.20, 6.85), 0.17),
    ((1.20, 0.30, 7.40), 0.12),
    ((3.40, 0.40, 7.80), 0.08),
    ((5.50, 0.45, 8.10), 0.035),
], soft_star, twist_total=math.radians(190))
# C: center fork going up
limb('limbC', [
    ((-3.75, -0.05, 5.50), 0.18),
    ((-3.20, -0.25, 6.40), 0.13),
    ((-2.90, -0.35, 7.30), 0.08),
    ((-2.70, -0.30, 8.20), 0.035),
], soft_star, twist_total=math.radians(120))
# D: lower drooping branch, mid-right
limb('limbD', [
    ((-4.05, -0.10, 5.20), 0.13),
    ((-3.00, -0.60, 5.20), 0.09),
    ((-2.00, -1.10, 5.05), 0.05),
    ((-1.20, -1.40, 4.80), 0.02),
], soft_star, twist_total=math.radians(100))
# E: rear depth branch
limb('limbE', [
    ((-3.90, 0.10, 5.40), 0.14),
    ((-3.40, 0.80, 6.20), 0.09),
    ((-3.00, 1.50, 7.00), 0.05),
    ((-2.80, 2.00, 7.70), 0.02),
], soft_star, twist_total=math.radians(100))

# twigs at distal tips
twig_specs = [
    ('twA1', (-5.50, 0.30, 7.3), (-6.1, 0.9, 7.9)),
    ('twA2', (-5.80, 0.35, 7.6), (-6.3, -0.3, 8.2)),
    ('twB1', (-0.80, 0.20, 6.85), (-0.5, 0.9, 7.5)),
    ('twB2', (1.20, 0.30, 7.40), (1.6, -0.4, 8.0)),
    ('twB3', (3.40, 0.40, 7.80), (4.0, 1.0, 8.3)),
    ('twB4', (2.20, 0.35, 7.60), (2.6, 0.95, 8.15)),
    ('twC1', (-2.90, -0.35, 7.30), (-3.4, -0.9, 8.0)),
    ('twC2', (-2.80, -0.33, 7.80), (-2.2, -0.8, 8.5)),
    ('twD1', (-2.00, -1.10, 5.05), (-1.5, -1.8, 5.4)),
    ('twE1', (-3.00, 1.50, 7.00), (-3.4, 2.2, 7.5)),
    ('twE2', (-2.85, 1.70, 7.30), (-2.2, 2.3, 7.9)),
]
for name, a, b in twig_specs:
    mid = ((a[0]+b[0])/2 + 0.08, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.15)
    limb(name, [(a, 0.045), (mid, 0.028), (b, 0.011)], soft_star, twist_total=math.radians(60))

# join
bpy.ops.object.select_all(action='DESELECT')
limbs = [o for o in tree_col.objects if o.type == 'CURVE']
for o in limbs:
    o.select_set(True)
bpy.context.view_layer.objects.active = limbs[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join()
trunk = bpy.context.object
trunk.name = 'MapleTree'
trunk.data.materials.clear()
trunk.data.materials.append(bark)
for p in trunk.data.polygons:
    p.use_smooth = True
trunk.location.z = -0.35

tex = bpy.data.textures.get('gnarl') or bpy.data.textures.new('gnarl', 'CLOUDS')
tex.noise_scale = 0.5
disp = trunk.modifiers.new('gnarl', 'DISPLACE')
disp.texture = tex
disp.strength = 0.035
disp.texture_coords = 'GLOBAL'
subd = trunk.modifiers.new('subd', 'SUBSURF')
subd.levels = 1
subd.render_levels = 1

# ---------- isolate & render ----------
for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    lc.exclude = lc.name not in ('TREE', 'LEAF_STUDIO')

cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = False
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1400
s.render.resolution_percentage = 100

# mid shot: whole bare tree silhouette vs backdrop
cam.data.lens = 42
cam.location = (-1.2, -14.0, 4.6)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p12_tree_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED mid')

save()
print('P12 DONE')
