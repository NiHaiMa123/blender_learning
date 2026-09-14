"""Phase 20: iteration 6 — BarkFine: 3x finer texture scale + lower contrast on limbs."""
import bpy, math, sys, random
from mathutils import Vector, Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR
import os
random.seed(21)

for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    if lc.name in ('TREE', 'LEAF_STUDIO', 'TREE_VIEW_LIGHTS'):
        lc.exclude = False

for o in list(bpy.data.collections.get('TREE').objects):
    bpy.data.objects.remove(o, do_unlink=True)

deep_star = bpy.data.objects['StarDeep']
soft_star = bpy.data.objects['StarSoft']
bark = bpy.data.materials['Bark']
# fine variant for limbs: same photo bark, half bump so thin branches don't
# look like cracked dry mud
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
        n.inputs['Brightness'].default_value = -0.14
        n.inputs['Contrast'].default_value = 0.0
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

# ---------- MASSIVE bole: broad open S, stays fat, gentler twist ----------
limb('trunk', [
    ((-4.50, 0.00, -0.8), 1.30),
    ((-5.00, 0.00, 0.8), 1.16),
    ((-5.65, 0.05, 2.3), 1.02),
    ((-5.60, 0.10, 3.6), 0.98),
    ((-5.05, 0.12, 4.7), 0.85),
    ((-4.35, 0.10, 5.6), 0.72),
    ((-3.80, 0.05, 6.2), 0.52),
], deep_star, twist_total=math.radians(100))

# roots: big flares
for i, ang in enumerate((-0.7, 0.4, 2.5, 3.7)):
    dx, dy = math.cos(ang) * 1.55, math.sin(ang) * 1.25
    limb(f'root{i}', [
        ((-4.62, 0.0, 0.45), 0.52),
        ((-4.62 + dx * 0.45, dy * 0.45, 0.02), 0.30),
        ((-4.62 + dx * 0.8, dy * 0.8, -0.30), 0.17),
        ((-4.62 + dx, dy, -0.75), 0.10),
    ], soft_star, twist_total=math.radians(45), mat=bark_fine)

# ---------- limbs — fatter, more of them ----------
# A: up-left, exits top-left
limb('limbA', [
    ((-3.95, 0.05, 6.00), 0.50),
    ((-4.80, 0.15, 6.9), 0.38),
    ((-5.65, 0.30, 7.7), 0.28),
    ((-6.60, 0.40, 8.5), 0.18),
    ((-7.50, 0.45, 9.2), 0.09),
], soft_star, twist_total=math.radians(35), mat=bark_fine)
# A2: sub-branch off A going up
limb('limbA2', [
    ((-5.65, 0.30, 7.7), 0.16),
    ((-5.40, 0.85, 8.45), 0.11),
    ((-5.15, 1.25, 9.15), 0.05),
], soft_star, twist_total=math.radians(30), mat=bark_fine)
# B: THE big right sweep — thick base, long, slight droop at tip
limb('limbB', [
    ((-3.65, 0.00, 5.95), 0.66),
    ((-2.10, 0.10, 6.30), 0.52),
    ((-0.30, 0.20, 6.75), 0.40),
    ((1.80, 0.30, 7.10), 0.30),
    ((4.10, 0.40, 7.25), 0.20),
    ((6.40, 0.45, 7.10), 0.09),
], soft_star, twist_total=math.radians(80), mat=bark_fine)
# B2: second tier on the right sweep, forking mid-way (like reference)
limb('limbB2', [
    ((0.60, 0.28, 6.95), 0.24),
    ((1.90, 0.75, 7.70), 0.17),
    ((3.20, 1.00, 8.40), 0.11),
    ((4.40, 1.10, 9.00), 0.05),
], soft_star, twist_total=math.radians(45), mat=bark_fine)
# B3: drooping sub-branch under the right sweep
limb('limbB3', [
    ((2.40, 0.35, 7.15), 0.15),
    ((3.20, -0.35, 6.70), 0.10),
    ((3.90, -0.80, 6.25), 0.04),
], soft_star, twist_total=math.radians(30), mat=bark_fine)
# C: center fork going up
limb('limbC', [
    ((-3.85, -0.05, 5.90), 0.38),
    ((-3.30, -0.25, 6.85), 0.28),
    ((-3.00, -0.35, 7.75), 0.18),
    ((-2.80, -0.30, 8.60), 0.08),
], soft_star, twist_total=math.radians(55), mat=bark_fine)
# C2: sub-branch off C going right-up
limb('limbC2', [
    ((-3.10, -0.30, 7.40), 0.14),
    ((-2.30, -0.55, 8.00), 0.09),
    ((-1.60, -0.70, 8.55), 0.04),
], soft_star, twist_total=math.radians(30), mat=bark_fine)
# D: lower drooping branch, mid-right (thicker, hangs lower)
limb('limbD', [
    ((-4.15, -0.10, 5.30), 0.30),
    ((-3.10, -0.55, 5.10), 0.22),
    ((-2.10, -1.00, 4.80), 0.13),
    ((-1.30, -1.35, 4.35), 0.05),
], soft_star, twist_total=math.radians(45), mat=bark_fine)
# E: rear depth branch
limb('limbE', [
    ((-3.95, 0.15, 5.70), 0.30),
    ((-3.45, 0.85, 6.55), 0.20),
    ((-3.05, 1.55, 7.35), 0.12),
    ((-2.85, 2.05, 8.05), 0.05),
], soft_star, twist_total=math.radians(45), mat=bark_fine)
# F: small branch forward-left mid height (fills left gap)
limb('limbF', [
    ((-5.05, -0.05, 4.90), 0.22),
    ((-5.55, -0.60, 5.55), 0.14),
    ((-6.00, -1.00, 6.20), 0.06),
], soft_star, twist_total=math.radians(35), mat=bark_fine)

# ---------- second-order branches along each limb (crown density) ----------
second_order = [
    # (name, base_point, tip, base_r, tip_r)
    ('sA1', (-4.80, 0.15, 6.9), (-5.20, -0.75, 7.6), 0.14, 0.04),
    ('sA2', (-5.65, 0.30, 7.7), (-6.35, -0.55, 8.1), 0.12, 0.05),
    ('sA3', (-4.80, 0.15, 6.9), (-4.35, 0.95, 7.75), 0.13, 0.04),
    ('sB1', (-2.10, 0.10, 6.30), (-2.35, -0.85, 6.9), 0.16, 0.05),
    ('sB2', (-0.30, 0.20, 6.75), (-0.55, -0.75, 7.45), 0.14, 0.04),
    ('sB3', (1.80, 0.30, 7.10), (1.55, 1.15, 7.8), 0.13, 0.04),
    ('sB4', (4.10, 0.40, 7.25), (4.55, -0.35, 7.75), 0.11, 0.05),
    ('sB5', (-2.10, 0.10, 6.30), (-1.55, 0.95, 6.95), 0.15, 0.04),
    ('sB6', (0.60, 0.28, 6.95), (0.85, -0.55, 7.6), 0.12, 0.05),
    ('sC1', (-3.30, -0.25, 6.85), (-3.95, -0.85, 7.5), 0.13, 0.04),
    ('sC2', (-3.00, -0.35, 7.75), (-3.55, -0.20, 8.5), 0.10, 0.05),
    ('sD1', (-3.10, -0.55, 5.10), (-3.35, -1.45, 5.65), 0.10, 0.05),
    ('sE1', (-3.45, 0.85, 6.55), (-4.15, 1.45, 7.05), 0.10, 0.05),
    ('sE2', (-3.05, 1.55, 7.35), (-3.75, 2.25, 7.75), 0.08, 0.04),
    ('sF1', (-5.55, -0.60, 5.55), (-6.25, -0.35, 6.1), 0.08, 0.04),
]
for name, a, b, ra, rb in second_order:
    mid = ((a[0]+b[0])/2 + 0.06, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.12)
    limb(name, [(a, ra), (mid, (ra+rb)/2), (b, rb)], soft_star,
         twist_total=math.radians(50), mat=bark_fine)

# twigs — 2 per distal section
twig_specs = [
    ('twA1', (-5.65, 0.30, 7.7), (-6.25, 0.95, 8.3)),
    ('twA2', (-6.00, 0.35, 7.9), (-6.60, -0.25, 8.5)),
    ('twA3', (-6.60, 0.40, 8.5), (-7.2, 0.95, 9.05)),
    ('twB1', (-0.30, 0.20, 6.75), (0.05, 0.95, 7.35)),
    ('twB2', (1.80, 0.30, 7.10), (2.25, -0.35, 7.70)),
    ('twB3', (4.10, 0.40, 7.25), (4.75, 1.05, 7.75)),
    ('twB4', (2.90, 0.35, 7.18), (3.35, 0.95, 7.85)),
    ('twB5', (5.30, 0.42, 7.18), (5.90, 1.00, 7.68)),
    ('twC1', (-3.00, -0.35, 7.75), (-3.45, -0.95, 8.45)),
    ('twC2', (-2.90, -0.33, 8.15), (-2.30, -0.85, 8.85)),
    ('twD1', (-2.10, -1.00, 4.80), (-1.60, -1.75, 5.15)),
    ('twE1', (-3.05, 1.55, 7.35), (-3.50, 2.25, 7.90)),
    ('twE2', (-2.90, 1.75, 7.65), (-2.25, 2.35, 8.25)),
    ('twF1', (-5.55, -0.60, 5.55), (-6.05, -1.30, 6.00)),
    ('twB6', (0.60, 0.28, 6.95), (0.95, -0.40, 7.45)),
    ('twC3', (-2.85, -0.32, 8.35), (-2.45, 0.30, 8.95)),
]
for name, a, b in twig_specs:
    mid = ((a[0]+b[0])/2 + 0.08, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.15)
    limb(name, [(a, 0.06), (mid, 0.038), (b, 0.030)], soft_star,
         twist_total=math.radians(50), mat=bark_fine)

# join limbs
bpy.ops.object.select_all(action='DESELECT')
limbs = [o for o in tree_col.objects if o.type == 'CURVE']
for o in limbs:
    o.select_set(True)
bpy.context.view_layer.objects.active = limbs[0]
bpy.ops.object.convert(target='MESH')
bpy.ops.object.join()
trunk = bpy.context.object
trunk.name = 'MapleTree'
# keep per-face material slots (bark on trunk, bark_fine on limbs) — do NOT clear
for p in trunk.data.polygons:
    p.use_smooth = True
trunk.location.z = -0.35

# ---------- collars: subtle embedded bulges ----------
collars = [
    (-3.92, 0.10, 5.95, 0.20),
    (-3.75, 0.08, 5.88, 0.22),
    (-3.85, -0.02, 5.82, 0.14),
    (-4.10, -0.05, 5.28, 0.13),
    (-3.95, 0.16, 5.66, 0.13),
    (-5.02, -0.03, 4.88, 0.11),
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

# ---------- hollow on inner S bend ----------
hollow_mat = bpy.data.materials.get('HollowDark') or bpy.data.materials.new('HollowDark')
hollow_mat.use_nodes = True
hb = next(n for n in hollow_mat.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
hb.inputs['Base Color'].default_value = (0.0004, 0.0003, 0.0002, 1)
hb.inputs['Roughness'].default_value = 1.0
hb.inputs['Specular IOR Level'].default_value = 0.0

bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(-5.62, -0.72, 3.30))
hol = bpy.context.object
hol.name = 'TrunkHollow'
hol.scale = (0.34, 0.15, 0.50)
hol.rotation_euler = Euler((math.radians(-15), math.radians(25), math.radians(12)), 'XYZ')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for uc in list(hol.users_collection):
    uc.objects.unlink(hol)
tree_col.objects.link(hol)
hol.data.materials.append(hollow_mat)
for p in hol.data.polygons:
    p.use_smooth = True
bpy.ops.mesh.primitive_torus_add(major_radius=0.27, minor_radius=0.07,
                                 major_segments=24, minor_segments=8,
                                 location=(-5.64, -0.75, 3.30),
                                 rotation=(math.radians(90), math.radians(8), 0))
rim = bpy.context.object
rim.name = 'HollowRim'
rim.scale = (0.82, 0.95, 1.55)
rim.rotation_euler.z = math.radians(-14)
for uc in list(rim.users_collection):
    uc.objects.unlink(rim)
tree_col.objects.link(rim)
rim.data.materials.append(bark)
for p in rim.data.polygons:
    p.use_smooth = True

# gentle gnarl + subdivision
tex = bpy.data.textures.get('gnarl') or bpy.data.textures.new('gnarl', 'CLOUDS')
tex.noise_scale = 0.5
disp = trunk.modifiers.new('gnarl', 'DISPLACE')
disp.texture = tex
disp.strength = 0.03
disp.texture_coords = 'GLOBAL'
subd = trunk.modifiers.new('subd', 'SUBSURF')
subd.levels = 1
subd.render_levels = 1

# ---------- isolate & mid render only ----------
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
s.render.filepath = os.path.join(RENDER_DIR, 'p20_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED p17_mid')

save()
print('P20 DONE')
