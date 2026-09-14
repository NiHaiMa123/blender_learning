exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
random.seed(11)

# ---------- cleanup on rerun ----------
for cname in ('TREE', 'CANOPY'):
    c = bpy.data.collections.get(cname)
    if c:
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
for o in ('PH_trunk', 'PH_canopy'):
    ob = bpy.data.objects.get(o)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)

tree_col = col('TREE')
can_col = col('CANOPY')

# ---------- bark material ----------
def bark_material():
    m = bpy.data.materials.get('Bark') or bpy.data.materials.new('Bark')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 4.0
    tex.inputs['Detail'].default_value = 5.0
    tex.inputs['Roughness'].default_value = 0.75
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.008, 0.003, 0.002, 1)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[1].color = (0.05, 0.02, 0.012, 1)
    ramp.color_ramp.elements[1].position = 0.8
    bump_tex = nt.nodes.new('ShaderNodeTexNoise')
    bump_tex.inputs['Scale'].default_value = 55.0
    bump_tex.inputs['Detail'].default_value = 3.0
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.55
    bump.inputs['Distance'].default_value = 0.06
    bsdf.inputs['Roughness'].default_value = 0.92
    nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bump_tex.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

bark = bark_material()

# ---------- curve limb builder ----------
def limb(name, pts, col_=tree_col):
    """pts: [(co, radius), ...] smooth bezier tube"""
    cu = bpy.data.curves.new(name + '_cu', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 1.0
    cu.bevel_resolution = 3
    cu.resolution_u = 8
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, (co, r) in zip(sp.bezier_points, pts):
        bp.co = co
        bp.radius = r
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    col_.objects.link(o)
    o.data.materials.append(bark)
    return o

# ---------- skeleton: gnarled S-trunk + right-sweeping main limb ----------
# main trunk spine: base -> lean left -> curl right into split
limb('trunk', [
    ((-4.65, 0.0, -0.4), 0.62),
    ((-4.75, 0.0, 0.6), 0.55),
    ((-5.00, 0.1, 1.7), 0.47),
    ((-4.95, 0.15, 2.9), 0.40),
    ((-4.55, 0.12, 4.0), 0.33),
    ((-3.95, 0.05, 5.0), 0.27),
    ((-3.55, 0.0, 5.6), 0.20),
])

# roots flare
for i, ang in enumerate((-0.6, 0.5, 2.6, 3.6)):
    dx, dy = math.cos(ang) * 1.15, math.sin(ang) * 0.9
    limb(f'root{i}', [
        ((-4.7, 0.0, 0.5), 0.28),
        ((-4.7 + dx * 0.6, dy * 0.6, 0.12), 0.16),
        ((-4.7 + dx, dy, -0.25), 0.05),
    ])

# limb A: up-left, exits top-left frame
limb('limbA', [
    ((-3.7, 0.02, 5.3), 0.22),
    ((-4.35, 0.15, 6.1), 0.17),
    ((-5.1, 0.3, 7.0), 0.12),
    ((-6.0, 0.4, 7.9), 0.07),
    ((-6.9, 0.45, 8.6), 0.03),
])
# limb B: the long right sweep across the top
limb('limbB', [
    ((-3.6, 0.0, 5.5), 0.24),
    ((-2.3, 0.1, 6.15), 0.19),
    ((-0.6, 0.2, 6.8), 0.14),
    ((1.4, 0.3, 7.35), 0.10),
    ((3.5, 0.4, 7.7), 0.06),
    ((5.3, 0.45, 8.0), 0.025),
])
# limb C: center fork going up
limb('limbC', [
    ((-3.7, -0.05, 5.5), 0.15),
    ((-3.1, -0.25, 6.4), 0.11),
    ((-2.7, -0.35, 7.4), 0.07),
    ((-2.5, -0.3, 8.3), 0.03),
])
# limb D: lower drooping branch (visible against sky, mid-left)
limb('limbD', [
    ((-3.9, -0.1, 5.2), 0.11),
    ((-3.0, -0.7, 5.3), 0.075),
    ((-2.0, -1.2, 5.15), 0.045),
    ((-1.2, -1.5, 4.9), 0.02),
])
# limb E: rear branch for depth
limb('limbE', [
    ((-3.8, 0.05, 5.4), 0.12),
    ((-3.2, 0.8, 6.1), 0.08),
    ((-2.6, 1.5, 6.9), 0.05),
    ((-2.2, 2.0, 7.6), 0.02),
])

# twigs at distal sections (leaf-spray supports)
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
    mid = ((a[0] + b[0]) / 2 + 0.08, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2 + 0.15)
    limb(name, [(a, 0.035), (mid, 0.02), (b, 0.008)])

# ---------- convert curves to joined mesh + displace gnarl ----------
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

# gnarl displacement
tex = bpy.data.textures.get('gnarl') or bpy.data.textures.new('gnarl', 'CLOUDS')
tex.noise_scale = 0.35
disp = trunk.modifiers.new('gnarl', 'DISPLACE')
disp.texture = tex
disp.strength = 0.07
disp.texture_coords = 'GLOBAL'
subd = trunk.modifiers.new('subd', 'SUBSURF')
subd.levels = 1
subd.render_levels = 1

# ---------- canopy emitter puffs ----------
puff_specs = [
    # (center, radius, squash_z)  upper-left cluster (limb A)
    ((-5.9, 0.4, 8.2), 1.5, 0.75),
    ((-5.0, 0.2, 7.6), 1.3, 0.7),
    ((-6.6, 0.5, 8.9), 1.2, 0.8),
    # top band along limb B
    ((-2.9, 0.0, 6.9), 1.5, 0.7),
    ((-1.2, 0.3, 7.5), 1.6, 0.7),
    ((0.6, 0.4, 7.9), 1.7, 0.7),
    ((2.4, 0.5, 8.1), 1.6, 0.7),
    ((4.2, 0.6, 8.3), 1.5, 0.7),
    ((5.6, 0.6, 8.4), 1.1, 0.7),
    # center fork fill
    ((-2.7, -0.4, 8.2), 1.3, 0.75),
    ((-3.4, 0.6, 7.8), 1.2, 0.7),
    # lower hanging cluster (limb D)
    ((-1.6, -1.3, 5.4), 1.0, 0.8),
    ((-2.5, -0.9, 5.6), 0.85, 0.8),
    # rear depth
    ((-2.4, 1.8, 7.6), 1.2, 0.7),
    ((-3.1, 2.2, 8.0), 1.0, 0.7),
]
puffs = []
for i, (c, r, sz) in enumerate(puff_specs):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=2, location=c)
    p = bpy.context.object
    p.name = f'puff{i:02d}'
    p.scale.z = sz
    p.scale.y *= 0.85
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for uc in list(p.users_collection):
        uc.objects.unlink(p)
    can_col.objects.link(p)
    puffs.append(p)

bpy.ops.object.select_all(action='DESELECT')
for p in puffs:
    p.select_set(True)
bpy.context.view_layer.objects.active = puffs[0]
bpy.ops.object.join()
emitter = bpy.context.object
emitter.name = 'CanopyEmitter'
emitter.display_type = 'WIRE'

# ---------- GN: scatter leaves on puff surfaces ----------
def leaf_scatter_gn(name='GN_Canopy'):
    ng = bpy.data.node_groups.get(name) or bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.nodes.clear()
    # interface (blender 4/5 style)
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    inp = ng.nodes.new('NodeGroupInput')
    outp = ng.nodes.new('NodeGroupOutput')
    dist = ng.nodes.new('GeometryNodeDistributePointsOnFaces')
    dist.inputs['Density'].default_value = 160.0
    coll = ng.nodes.new('GeometryNodeCollectionInfo')
    coll.inputs['Collection'].default_value = bpy.data.collections['LEAF_SRC']
    coll.inputs['Separate Children'].default_value = True
    coll.inputs['Reset Children'].default_value = True
    inst = ng.nodes.new('GeometryNodeInstanceOnPoints')
    inst.inputs['Pick Instance'].default_value = True
    rnd_rot = ng.nodes.new('FunctionNodeRandomValue')
    rnd_rot.data_type = 'FLOAT_VECTOR'
    rnd_rot.inputs['Min'].default_value = (-math.pi, -math.pi, -math.pi)
    rnd_rot.inputs['Max'].default_value = (math.pi, math.pi, math.pi)
    rnd_scl = ng.nodes.new('FunctionNodeRandomValue')
    rnd_scl.data_type = 'FLOAT'
    rnd_scl.inputs['Min'].default_value = 0.75
    rnd_scl.inputs['Max'].default_value = 1.35
    ng.links.new(inp.outputs['Geometry'], dist.inputs['Mesh'])
    ng.links.new(dist.outputs['Points'], inst.inputs['Points'])
    ng.links.new(coll.outputs['Instances'], inst.inputs['Instance'])
    ng.links.new(rnd_rot.outputs['Value'], inst.inputs['Rotation'])
    ng.links.new(rnd_scl.outputs['Value'], inst.inputs['Scale'])
    ng.links.new(inst.outputs['Instances'], outp.inputs['Geometry'])
    inp.location = (-400, 0); outp.location = (400, 0)
    return ng

gn = leaf_scatter_gn()
mod = emitter.modifiers.new('leafscatter', 'NODES')
mod.node_group = gn

save()
render_preview('p03_tree_eevee.png', pct=50)
