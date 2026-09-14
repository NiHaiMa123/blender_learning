"""Phase 26: harden elbow (knuckle bulge), swollen shoulder at limbR,
buttress roots, wider upper trunk."""
import bpy, math, sys, random
from mathutils import Vector, Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR
import os
random.seed(25)

for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    if lc.name in ('TREE', 'LEAF_STUDIO', 'TREE_VIEW_LIGHTS'):
        lc.exclude = False

for o in list(bpy.data.collections.get('TREE').objects):
    bpy.data.objects.remove(o, do_unlink=True)

deep_star = bpy.data.objects['StarDeep']
soft_star = bpy.data.objects['StarSoft']
bark = bpy.data.materials['Bark']
bark_fine = bpy.data.materials.get('BarkFine') or bark
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

BX = -4.4          # base center x
Ht = 7.2           # visible trunk height per spec

# ---------- TRUNK: measured switchback profile ----------
# (z/Ht, dx/Ht, r/Ht) from spec -> world (BX+dx*Ht, z*Ht-0.2, r*Ht)
trunk_spec = [
    (0.00,  0.00, 0.090),
    (0.15, -0.06, 0.080),
    (0.35, -0.10, 0.072),
    (0.50, -0.13, 0.070),
    (0.55, -0.16, 0.080),   # ELBOW knuckle — radius swell makes a step
    (0.62, -0.13, 0.062),
    (0.68, -0.08, 0.058),   # right edge concave
    (0.85, -0.04, 0.056),
    (1.00, -0.10, 0.042),   # top kinks left into co-leader
]
limb('trunk', [
    ((BX + dx * Ht, 0.0, zn * Ht - 0.2), r * Ht)
    for zn, dx, r in trunk_spec
], soft_star, twist_total=math.radians(55))

# roots: modest flares, buried
# roots: broad flat buttresses melting into ground (not claws)
for i, ang in enumerate((-0.9, -0.1, 0.9, 2.3, 3.4, 4.4)):
    dx, dy = math.cos(ang) * 1.5, math.sin(ang) * 1.3
    limb(f'root{i}', [
        ((BX - 0.05, 0.0, 0.55), 0.34),
        ((BX - 0.05 + dx * 0.35, dy * 0.35, 0.12), 0.24),
        ((BX - 0.05 + dx * 0.65, dy * 0.65, -0.18), 0.14),
        ((BX - 0.05 + dx, dy, -0.55), 0.08),
    ], soft_star, twist_total=math.radians(30), mat=bark_fine)

# ---------- LIMBS: few, long, smooth ----------
# limbR — THE signature horizontal limb off right side at 0.68Ht
limb('limbR', [
    ((BX - 0.35,  0.05, 4.75), 0.36),
    ((BX + 0.60,  0.15, 4.80), 0.30),
    ((BX + 1.70,  0.25, 4.95), 0.24),
    ((BX + 2.80,  0.35, 5.25), 0.18),
    ((BX + 3.80,  0.42, 5.70), 0.12),
    ((BX + 4.60,  0.45, 6.20), 0.05),
], soft_star, twist_total=math.radians(30), mat=bark_fine)
# limbR forks near its end (visible V at right in ref)
limb('limbR2', [
    ((BX + 2.80, 0.35, 5.25), 0.15),
    ((BX + 3.60, 0.90, 5.60), 0.10),
    ((BX + 4.30, 1.30, 6.05), 0.04),
], soft_star, twist_total=math.radians(25), mat=bark_fine)

# coLeader — trunk continues up-left steeply
limb('coLeader', [
    ((BX - 0.72, 0.05, 6.90), 0.30),
    ((BX - 1.35, 0.15, 7.75), 0.24),
    ((BX - 2.10, 0.28, 8.50), 0.17),
    ((BX - 2.90, 0.38, 9.15), 0.10),
    ((BX - 3.60, 0.45, 9.70), 0.04),
], soft_star, twist_total=math.radians(30), mat=bark_fine)

# limbUp — near-vertical second leader right of coLeader
limb('limbUp', [
    ((BX - 0.45, -0.05, 6.75), 0.28),
    ((BX - 0.55, -0.15, 7.80), 0.21),
    ((BX - 0.50, -0.20, 8.80), 0.13),
    ((BX - 0.30, -0.20, 9.60), 0.05),
], soft_star, twist_total=math.radians(30), mat=bark_fine)

# limbD — drooping branch off lower-left, hangs down-left (ref left edge)
limb('limbD', [
    ((BX - 0.85, -0.05, 3.30), 0.20),
    ((BX - 1.55, -0.35, 2.95), 0.14),
    ((BX - 2.15, -0.70, 2.55), 0.08),
    ((BX - 2.60, -1.00, 2.10), 0.03),
], soft_star, twist_total=math.radians(25), mat=bark_fine)

# limbBack — rear depth limb at fork
limb('limbBack', [
    ((BX - 0.55, 0.15, 6.30), 0.22),
    ((BX - 0.15, 0.95, 7.10), 0.15),
    ((BX + 0.20, 1.65, 7.90), 0.09),
    ((BX + 0.45, 2.10, 8.55), 0.03),
], soft_star, twist_total=math.radians(25), mat=bark_fine)

# ---------- sparse long secondaries ----------
second_order = [
    ('sR1', (BX + 0.60, 0.15, 4.80), (BX + 0.85, -0.90, 5.55), 0.12, 0.04),
    ('sR2', (BX + 1.70, 0.25, 4.95), (BX + 2.00, 1.15, 5.60), 0.11, 0.03),
    ('sL1', (BX - 1.35, 0.15, 7.75), (BX - 1.95, -0.75, 8.35), 0.11, 0.03),
    ('sL2', (BX - 2.10, 0.28, 8.50), (BX - 2.65, 1.05, 9.10), 0.09, 0.03),
    ('sU1', (BX - 0.55, -0.15, 7.80), (BX + 0.30, -0.70, 8.55), 0.10, 0.03),
    ('sB1', (BX - 0.15, 0.95, 7.10), (BX - 0.95, 1.55, 7.80), 0.09, 0.03),
]
for name, a, b, ra, rb in second_order:
    mid = ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.18)
    limb(name, [(a, ra), (mid, (ra+rb)/2), (b, rb)], soft_star,
         twist_total=math.radians(25), mat=bark_fine)

# a few long twigs at tips
twig_specs = [
    ('twR1', (BX + 3.80, 0.42, 5.70), (BX + 4.50, -0.10, 6.15)),
    ('twR2', (BX + 2.80, 0.35, 5.25), (BX + 3.45, -0.35, 5.85)),
    ('twL1', (BX - 2.90, 0.38, 9.15), (BX - 3.45, -0.20, 9.70)),
    ('twU1', (BX - 0.30, -0.20, 9.60), (BX + 0.25, -0.75, 10.10)),
    ('twU2', (BX - 0.50, -0.20, 8.80), (BX - 1.30, -0.80, 9.35)),
    ('twD1', (BX - 2.15, -0.70, 2.55), (BX - 2.75, -0.30, 2.90)),
]
for name, a, b in twig_specs:
    mid = ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.10)
    limb(name, [(a, 0.045), (mid, 0.028), (b, 0.018)], soft_star,
         twist_total=math.radians(20), mat=bark_fine)

# join — keep per-face material slots
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
trunk.location.z = -0.15

# minimal collars — just smooth the fork zone
collars = [
    (BX - 0.30, 0.06, 4.72, 0.40),   # limbR shoulder — big swollen union
    (BX - 0.50, 0.05, 6.35, 0.22),
    (BX - 0.55, 0.10, 6.55, 0.20),
    (BX - 0.80, -0.03, 3.30, 0.13),
    (BX - 0.75, 0.02, 3.85, 0.16),   # elbow knuckle pad
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
tex.noise_scale = 0.6
disp = trunk.modifiers.new('gnarl', 'DISPLACE')
disp.texture = tex
disp.strength = 0.02
disp.texture_coords = 'GLOBAL'
subd = trunk.modifiers.new('subd', 'SUBSURF')
subd.levels = 1
subd.render_levels = 1

# isolate & mid render
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
d = Vector((-3.2, 0.1, 4.6)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
s.render.filepath = os.path.join(RENDER_DIR, 'p26_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED p26_mid')

save()
print('P26 DONE')
