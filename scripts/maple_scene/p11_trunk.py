"""Phase 11: twisted muscle-ridge trunk (reference: hornbeam-style sinuous
ridges wrapping the S-curve, smooth dark maple bark, gold-green moss).

Technique: star/lobed 2D profile as curve bevel_object + per-point tilt
ramping along the spline -> helical ridges. Then isolate & closeup render.
"""
import bpy, bmesh, math, sys
from mathutils import Vector, Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, move_to_col, save, RENDER_DIR
import os, random
random.seed(11)

# ---------- ensure TREE + LEAF_STUDIO are in view layer first ----------
for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    if lc.name in ('TREE', 'LEAF_STUDIO'):
        lc.exclude = False

# ---------- clean old tree ----------
for o in list(bpy.data.collections.get('TREE').objects):
    bpy.data.objects.remove(o, do_unlink=True)
old = bpy.data.objects.get('MapleTree')
if old:
    bpy.data.objects.remove(old, do_unlink=True)

# ---------- star cross-section profiles ----------
def star_profile(name, lobes=6, inner=0.68, pts_per_lobe=4):
    cu = bpy.data.curves.get(name) or bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.resolution_u = 2
    cu.render_resolution_u = 2
    cu.twist_smooth = True
    sp = cu.splines.new('NURBS')
    n = lobes * pts_per_lobe
    sp.points.add(n - 1)
    for i in range(n):
        a = 2 * math.pi * i / n
        # alternate lobe tip / valley with smooth interpolation
        ph = (i % pts_per_lobe) / pts_per_lobe
        r = inner + (1 - inner) * (0.5 - 0.5 * math.cos(2 * math.pi * ph))
        sp.points[i].co = (math.cos(a) * r, math.sin(a) * r, 0, 1)
    sp.use_cyclic_u = True
    sp.order_u = 3
    sp.use_endpoint_u = False
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, cu)
    ob.data = cu
    if not ob.users_collection:
        col('LEAF_STUDIO').objects.link(ob)   # park profiles in studio (hidden from render anyway)
    ob.hide_render = True
    return ob

deep_star = star_profile('StarDeep', lobes=6, inner=0.62)
soft_star = star_profile('StarSoft', lobes=5, inner=0.80)

# ---------- bark + moss material ----------
def bark_material():
    m = bpy.data.materials.get('Bark') or bpy.data.materials.new('Bark')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.85

    # dark maple bark base -> subtle vertical furrow bump
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 3.0
    noise.inputs['Detail'].default_value = 4.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.006, 0.0025, 0.0018, 1)
    ramp.color_ramp.elements[0].position = 0.2
    ramp.color_ramp.elements[1].color = (0.045, 0.018, 0.010, 1)
    ramp.color_ramp.elements[1].position = 0.85
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])

    # moss: upfacing + noise mask -> gold-green
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mrg = nt.nodes.new('ShaderNodeMapRange')
    mrg.inputs['From Min'].default_value = 0.15
    mrg.inputs['From Max'].default_value = 0.75
    mrg.inputs['To Min'].default_value = 0.0
    mrg.inputs['To Max'].default_value = 1.0
    mrg.clamp = True
    moss_noise = nt.nodes.new('ShaderNodeTexNoise')
    moss_noise.inputs['Scale'].default_value = 2.2
    moss_noise.inputs['Detail'].default_value = 3.0
    mult = nt.nodes.new('ShaderNodeMath'); mult.operation = 'MULTIPLY'
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.inputs['B'].default_value = (0.10, 0.11, 0.015, 1)   # gold-green moss
    nt.links.new(geo.outputs['Normal'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Z'], mrg.inputs['Value'])
    nt.links.new(mrg.outputs['Result'], mult.inputs[0])
    nt.links.new(moss_noise.outputs['Fac'], mult.inputs[1])
    nt.links.new(mult.outputs[0], mix.inputs['Factor'])
    nt.links.new(ramp.outputs['Color'], mix.inputs['A'])
    nt.links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])

    # fine vertical furrow bump: stretched wave
    tex = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 6.0
    wave.inputs['Distortion'].default_value = 7.0
    wave.inputs['Detail'].default_value = 5.0
    wave.inputs['Detail Scale'].default_value = 2.0
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.05
    nt.links.new(tex.outputs['Generated'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    nt.links.new(wave.outputs['Color'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

bark = bark_material()

# ---------- limb builder with star bevel + tilt twist ----------
def limb(name, pts, profile, twist_total=0.0, col_=None):
    cu = bpy.data.curves.new(name + '_cu', 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 10
    cu.bevel_mode = 'OBJECT'
    cu.bevel_object = profile
    cu.bevel_resolution = 3
    cu.resolution_u = 10
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    n = len(pts)
    for i, (bp, (co, r)) in enumerate(zip(sp.bezier_points, pts)):
        bp.co = co
        bp.radius = r
        bp.tilt = twist_total * i / (n - 1)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    (col_ or col('TREE')).objects.link(o)
    o.data.materials.append(bark)
    return o

tree_col = col('TREE')

# ---------- skeleton (same poses as p03) ----------
limb('trunk', [
    ((-4.65, 0.0, -0.4), 0.68),
    ((-4.75, 0.0, 0.6), 0.58),
    ((-5.00, 0.1, 1.7), 0.50),
    ((-4.95, 0.15, 2.9), 0.42),
    ((-4.55, 0.12, 4.0), 0.34),
    ((-3.95, 0.05, 5.0), 0.27),
    ((-3.55, 0.0, 5.6), 0.20),
], deep_star, twist_total=math.radians(300))

for i, ang in enumerate((-0.6, 0.5, 2.6, 3.6)):
    dx, dy = math.cos(ang) * 1.25, math.sin(ang) * 1.0
    limb(f'root{i}', [
        ((-4.7, 0.0, 0.55), 0.34),
        ((-4.7 + dx * 0.55, dy * 0.55, 0.14), 0.20),
        ((-4.7 + dx, dy, -0.28), 0.06),
    ], deep_star, twist_total=math.radians(90))

limb('limbA', [
    ((-3.7, 0.02, 5.3), 0.24),
    ((-4.35, 0.15, 6.1), 0.18),
    ((-5.1, 0.3, 7.0), 0.13),
    ((-6.0, 0.4, 7.9), 0.08),
    ((-6.9, 0.45, 8.6), 0.035),
], soft_star, twist_total=math.radians(140))
limb('limbB', [
    ((-3.6, 0.0, 5.5), 0.26),
    ((-2.3, 0.1, 6.15), 0.20),
    ((-0.6, 0.2, 6.8), 0.15),
    ((1.4, 0.3, 7.35), 0.11),
    ((3.5, 0.4, 7.7), 0.07),
    ((5.3, 0.45, 8.0), 0.03),
], soft_star, twist_total=math.radians(180))
limb('limbC', [
    ((-3.7, -0.05, 5.5), 0.16),
    ((-3.1, -0.25, 6.4), 0.12),
    ((-2.7, -0.35, 7.4), 0.08),
    ((-2.5, -0.3, 8.3), 0.035),
], soft_star, twist_total=math.radians(120))
limb('limbD', [
    ((-3.9, -0.1, 5.2), 0.12),
    ((-3.0, -0.7, 5.3), 0.08),
    ((-2.0, -1.2, 5.15), 0.05),
    ((-1.2, -1.5, 4.9), 0.02),
], soft_star, twist_total=math.radians(100))
limb('limbE', [
    ((-3.8, 0.05, 5.4), 0.13),
    ((-3.2, 0.8, 6.1), 0.09),
    ((-2.6, 1.5, 6.9), 0.05),
    ((-2.2, 2.0, 7.6), 0.025),
], soft_star, twist_total=math.radians(100))

twig_specs = [
    ('twA1', (-5.1, 0.3, 7.0), (-5.7, 0.9, 7.7)),
    ('twA2', (-5.4, 0.35, 7.3), (-5.9, -0.3, 8.0)),
    ('twB1', (-0.6, 0.2, 6.8), (-0.3, 0.9, 7.5)),
    ('twB2', (1.4, 0.3, 7.35), (1.7, -0.4, 8.0)),
    ('twB3', (3.5, 0.4, 7.7), (4.1, 1.0, 8.3)),
    ('twB4', (2.4, 0.35, 7.5), (2.7, 0.9, 8.15)),
    ('twC1', (-2.7, -0.35, 7.4), (-3.2, -0.9, 8.1)),
    ('twC2', (-2.6, -0.33, 7.8), (-2.0, -0.8, 8.5)),
    ('twD1', (-2.0, -1.2, 5.15), (-1.5, -1.9, 5.5)),
    ('twE1', (-2.6, 1.5, 6.9), (-3.1, 2.2, 7.5)),
    ('twE2', (-2.4, 1.7, 7.2), (-1.8, 2.3, 7.9)),
]
for name, a, b in twig_specs:
    mid = ((a[0]+b[0])/2 + 0.08, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.15)
    limb(name, [(a, 0.04), (mid, 0.025), (b, 0.01)], soft_star, twist_total=math.radians(60))

# ---------- join to single mesh ----------
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

# gentle gnarl on top (smaller — ridges carry the form now)
tex = bpy.data.textures.get('gnarl') or bpy.data.textures.new('gnarl', 'CLOUDS')
tex.noise_scale = 0.5
disp = trunk.modifiers.new('gnarl', 'DISPLACE')
disp.texture = tex
disp.strength = 0.035
disp.texture_coords = 'GLOBAL'
subd = trunk.modifiers.new('subd', 'SUBSURF')
subd.levels = 1
subd.render_levels = 1

# ---------- isolate: TREE + LEAF_STUDIO only ----------
for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    lc.exclude = lc.name not in ('TREE', 'LEAF_STUDIO')

cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = False
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1400
s.render.resolution_percentage = 100
try:
    s.cycles.samples = 96
except Exception:
    pass

# shot 1: S-curve midsection
cam.data.lens = 50
cam.location = (-4.7, -5.2, 2.6)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p11_trunk_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED mid')

# shot 2: base + roots
cam.location = (-4.7, -3.2, 1.0)
cam.data.lens = 42
s.render.filepath = os.path.join(RENDER_DIR, 'p11_trunk_base.png')
bpy.ops.render.render(write_still=True)
print('RENDERED base')

save()
print('P11 DONE')
