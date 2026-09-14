"""Phase 22: outline match to reference — trunk LEANS left overall, low fork
at ~55% height, limbA upgraded to co-leader (near trunk thickness), hollow
removed. Mid-only render."""
import bpy, math, sys, random
from mathutils import Vector, Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR
import os
random.seed(22)

for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    if lc.name in ('TREE', 'LEAF_STUDIO', 'TREE_VIEW_LIGHTS'):
        lc.exclude = False

for o in list(bpy.data.collections.get('TREE').objects):
    bpy.data.objects.remove(o, do_unlink=True)

deep_star = bpy.data.objects['StarDeep']
soft_star = bpy.data.objects['StarSoft']
bark = bpy.data.materials['Bark']
bark_fine = bpy.data.materials.get('BarkFine')
if not bark_fine:
    bark_fine = bark.copy()
    bark_fine.name = 'BarkFine'
bump_i = 0
for n in bark_fine.node_tree.nodes:
    if n.bl_idname == 'ShaderNodeBump':
        n.inputs['Strength'].default_value = 0.12 if bump_i == 0 else 0.18
        n.inputs['Distance'].default_value = 0.02 if bump_i == 0 else 0.03
        bump_i += 1
    if n.bl_idname == 'ShaderNodeBrightContrast':
        n.inputs['Brightness'].default_value = -0.34
        n.inputs['Contrast'].default_value = 0.05
    if n.bl_idname == 'ShaderNodeMapping':
        n.inputs['Scale'].default_value = (7.0, 7.0, 2.2)
tree_col = col('TREE')

def limb(name, pts, profile, twist_total=0.0, mat=None):
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
        bp.radius = r * (1 + random.uniform(-0.03, 0.03))
        bp.tilt = twist_total * i / (n - 1)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    tree_col.objects.link(o)
    o.data.materials.append(mat or bark)
    return o

# ---------- BOLE: leans LEFT the whole way; left edge one long convex arc;
# right edge concave; fork low (~z 5.5). Reference silhouette. ----------
limb('trunk', [
    ((-4.20, 0.00, -1.0), 1.35),
    ((-4.55, 0.00,  0.4), 1.24),
    ((-5.05, 0.05,  1.8), 1.12),
    ((-5.40, 0.10,  3.2), 1.02),   # max left bulge
    ((-5.30, 0.12,  4.5), 0.90),   # still left; right edge concave here
    ((-4.85, 0.10,  5.6), 0.74),   # begins returning right
    ((-4.30, 0.05,  6.5), 0.58),   # fork zone
], deep_star, twist_total=math.radians(100))

# roots flare, buried
for i, ang in enumerate((-0.7, 0.4, 2.5, 3.7)):
    dx, dy = math.cos(ang) * 1.55, math.sin(ang) * 1.25
    limb(f'root{i}', [
        ((-4.45, 0.0, 0.35), 0.55),
        ((-4.45 + dx * 0.45, dy * 0.45, -0.05), 0.30),
        ((-4.45 + dx * 0.8, dy * 0.8, -0.35), 0.17),
        ((-4.45 + dx, dy, -0.80), 0.10),
    ], soft_star, twist_total=math.radians(45), mat=bark_fine)

# ---------- limbs ----------
# A: CO-LEADER — continues the trunk's leftward line, almost trunk-thick,
#    exits top-left. This is the signature silhouette element.
limb('limbA', [
    ((-4.40, 0.05, 6.30), 0.58),
    ((-5.10, 0.15, 7.10), 0.46),
    ((-5.95, 0.30, 7.85), 0.34),
    ((-6.95, 0.40, 8.55), 0.24),
    ((-7.95, 0.45, 9.15), 0.12),
], soft_star, twist_total=math.radians(35), mat=bark_fine)
# A2: sub-branch off A going up-right (fills crown top-center)
limb('limbA2', [
    ((-5.95, 0.30, 7.85), 0.18),
    ((-5.55, 0.85, 8.60), 0.12),
    ((-5.20, 1.25, 9.30), 0.05),
], soft_star, twist_total=math.radians(30), mat=bark_fine)
# B: big right sweep — thick, long, slight droop at tip
limb('limbB', [
    ((-4.35, 0.00, 6.15), 0.62),
    ((-2.80, 0.10, 6.45), 0.50),
    ((-0.90, 0.20, 6.80), 0.40),
    ((1.50, 0.30, 7.05), 0.30),
    ((4.10, 0.40, 7.15), 0.20),
    ((6.60, 0.45, 6.95), 0.09),
], soft_star, twist_total=math.radians(80), mat=bark_fine)
# B2: second tier right, forking mid-way
limb('limbB2', [
    ((0.30, 0.28, 6.90), 0.24),
    ((1.70, 0.75, 7.65), 0.17),
    ((3.10, 1.00, 8.30), 0.11),
    ((4.40, 1.10, 8.90), 0.05),
], soft_star, twist_total=math.radians(45), mat=bark_fine)
# B3: droop under the sweep
limb('limbB3', [
    ((2.20, 0.35, 7.10), 0.15),
    ((3.10, -0.35, 6.60), 0.10),
    ((3.85, -0.80, 6.10), 0.04),
], soft_star, twist_total=math.radians(30), mat=bark_fine)
# C: center fork going up
limb('limbC', [
    ((-4.50, -0.05, 6.20), 0.40),
    ((-3.95, -0.25, 7.10), 0.30),
    ((-3.55, -0.35, 7.95), 0.19),
    ((-3.25, -0.30, 8.80), 0.09),
], soft_star, twist_total=math.radians(55), mat=bark_fine)
# C2: sub-branch off C going right-up
limb('limbC2', [
    ((-3.65, -0.30, 7.55), 0.14),
    ((-2.80, -0.55, 8.15), 0.09),
    ((-2.05, -0.70, 8.65), 0.04),
], soft_star, twist_total=math.radians(30), mat=bark_fine)
# D: low drooping branch off the concave right edge — signature element
limb('limbD', [
    ((-4.75, -0.10, 5.45), 0.32),
    ((-3.70, -0.55, 5.20), 0.23),
    ((-2.70, -1.00, 4.85), 0.14),
    ((-1.85, -1.35, 4.40), 0.05),
], soft_star, twist_total=math.radians(45), mat=bark_fine)
# E: rear depth branch
limb('limbE', [
    ((-4.55, 0.15, 6.00), 0.30),
    ((-4.05, 0.85, 6.85), 0.20),
    ((-3.60, 1.55, 7.60), 0.12),
    ((-3.35, 2.05, 8.25), 0.05),
], soft_star, twist_total=math.radians(45), mat=bark_fine)
# F: front-left mid branch
limb('limbF', [
    ((-5.20, -0.05, 4.95), 0.22),
    ((-5.75, -0.60, 5.60), 0.14),
    ((-6.20, -1.00, 6.25), 0.06),
], soft_star, twist_total=math.radians(35), mat=bark_fine)

# ---------- second-order along limbs ----------
second_order = [
    ('sA1', (-5.10, 0.15, 7.10), (-5.55, -0.75, 7.75), 0.14, 0.04),
    ('sA2', (-5.95, 0.30, 7.85), (-6.65, -0.55, 8.30), 0.12, 0.03),
    ('sA3', (-5.10, 0.15, 7.10), (-4.60, 0.95, 7.90), 0.13, 0.04),
    ('sB1', (-2.80, 0.10, 6.45), (-3.05, -0.85, 7.05), 0.16, 0.05),
    ('sB2', (-0.90, 0.20, 6.80), (-1.15, -0.75, 7.45), 0.14, 0.04),
    ('sB3', (1.50, 0.30, 7.05), (1.25, 1.15, 7.75), 0.13, 0.04),
    ('sB4', (4.10, 0.40, 7.15), (4.60, -0.35, 7.60), 0.11, 0.03),
    ('sB5', (-2.80, 0.10, 6.45), (-2.20, 0.95, 7.05), 0.15, 0.04),
    ('sB6', (0.30, 0.28, 6.90), (0.60, -0.55, 7.55), 0.12, 0.03),
    ('sC1', (-3.95, -0.25, 7.10), (-4.55, -0.85, 7.75), 0.13, 0.04),
    ('sC2', (-3.55, -0.35, 7.95), (-4.05, -0.15, 8.70), 0.10, 0.03),
    ('sD1', (-3.70, -0.55, 5.20), (-3.90, -1.45, 5.75), 0.10, 0.03),
    ('sE1', (-4.05, 0.85, 6.85), (-4.70, 1.45, 7.30), 0.10, 0.03),
    ('sE2', (-3.60, 1.55, 7.60), (-4.25, 2.25, 7.95), 0.08, 0.02),
    ('sF1', (-5.75, -0.60, 5.55), (-6.45, -0.35, 6.10), 0.08, 0.02),
]
for name, a, b, ra, rb in second_order:
    mid = ((a[0]+b[0])/2 + 0.06, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.12)
    limb(name, [(a, ra), (mid, (ra+rb)/2), (b, rb)], soft_star,
         twist_total=math.radians(50), mat=bark_fine)

# twigs
twig_specs = [
    ('twA1', (-5.95, 0.30, 7.85), (-6.55, 0.95, 8.45)),
    ('twA2', (-6.30, 0.35, 8.10), (-6.90, -0.25, 8.70)),
    ('twA3', (-6.95, 0.40, 8.55), (-7.55, 0.95, 9.10)),
    ('twB1', (-0.90, 0.20, 6.80), (-0.55, 0.95, 7.40)),
    ('twB2', (1.50, 0.30, 7.05), (1.95, -0.35, 7.65)),
    ('twB3', (4.10, 0.40, 7.15), (4.75, 1.05, 7.65)),
    ('twB4', (2.90, 0.35, 7.10), (3.35, 0.95, 7.75)),
    ('twB5', (5.50, 0.42, 7.05), (6.10, 1.00, 7.50)),
    ('twC1', (-3.55, -0.35, 7.95), (-3.95, -0.95, 8.65)),
    ('twC2', (-3.40, -0.33, 8.35), (-2.80, -0.85, 9.05)),
    ('twD1', (-2.70, -1.00, 4.85), (-2.15, -1.75, 5.15)),
    ('twE1', (-3.60, 1.55, 7.60), (-4.05, 2.25, 8.10)),
    ('twE2', (-3.45, 1.75, 7.85), (-2.75, 2.35, 8.45)),
    ('twF1', (-5.75, -0.60, 5.55), (-6.25, -1.30, 6.05)),
    ('twB6', (0.30, 0.28, 6.90), (0.65, -0.40, 7.45)),
    ('twC3', (-3.35, -0.32, 8.55), (-2.90, 0.30, 9.15)),
]
for name, a, b in twig_specs:
    mid = ((a[0]+b[0])/2 + 0.08, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.15)
    limb(name, [(a, 0.06), (mid, 0.038), (b, 0.030)], soft_star,
         twist_total=math.radians(50), mat=bark_fine)

# join (keep per-face material slots)
bpy.ops.object.select_all(action='DESELECT')
limbs = [o for o in tree_col.objects if o.type == 'CURVE']
for o in limbs:
    o.select_set(True)
bpy.context.view_layer.objects.active = limbs[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join()
trunk = bpy.context.object
trunk.name = 'MapleTree'
for p in trunk.data.polygons:
    p.use_smooth = True
trunk.location.z = -0.35

# subtle collars only — no big bulge, just smooth union hints
collars = [
    (-4.38, 0.08, 6.25, 0.26),
    (-4.42, 0.05, 6.15, 0.28),
    (-4.50, -0.02, 6.10, 0.16),
    (-4.75, -0.05, 5.40, 0.16),
    (-4.55, 0.16, 5.95, 0.15),
    (-5.18, -0.03, 4.92, 0.12),
]
for i, (x, y, z, r) in enumerate(collars):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(x, y, z))
    s = bpy.context.object
    s.scale = (r, r * 0.55, r * 1.1)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for uc in list(s.users_collection):
        uc.objects.unlink(s)
    tree_col.objects.link(s)
    s.data.materials.append(bark)
    for p in s.data.polygons:
        p.use_smooth = True
bpy.ops.object.select_all(action='DESELECT')
for o in tree_col.objects:
    if o.type == 'MESH':
        o.select_set(True)
bpy.context.view_layer.objects.active = trunk
bpy.ops.object.join()
trunk = bpy.context.object
trunk.name = 'MapleTree'

tex = bpy.data.textures.get('gnarl') or bpy.data.textures.new('gnarl', 'CLOUDS')
tex.noise_scale = 0.5
disp = trunk.modifiers.new('gnarl', 'DISPLACE')
disp.texture = tex
disp.strength = 0.03
disp.texture_coords = 'GLOBAL'
subd = trunk.modifiers.new('subd', 'SUBSURF')
subd.levels = 1
subd.render_levels = 1

# isolate & render mid
for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    lc.exclude = lc.name not in ('TREE', 'LEAF_STUDIO', 'TREE_VIEW_LIGHTS')

cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = False
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1400
s.render.resolution_percentage = 100
cam.data.lens = 46
cam.location = (-1.6, -19.5, 4.8)
d = Vector((-3.0, 0.1, 4.4)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
s.render.filepath = os.path.join(RENDER_DIR, 'p22_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED p22_mid')

save()
print('P22 DONE')
