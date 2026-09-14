exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())
import bmesh

scene = bpy.context.scene
random.seed(23)
bg_col = col('BACKGROUND')
mid_col = col('MIDGROUND')

# ---------- materials ----------
def mat_simple(name, color, rough=0.9):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    return m

grass_m = mat_simple('Grass', (0.045, 0.11, 0.025), 0.95)
conifer_m = mat_simple('ConiferSil', (0.012, 0.035, 0.03), 0.95)
sil_m = mat_simple('Silhouette', (0.02, 0.03, 0.045), 0.95)
stone_m = mat_simple('Stone', (0.23, 0.22, 0.20), 0.85)
wood_m = mat_simple('Wood', (0.07, 0.045, 0.028), 0.9)
birch_m = mat_simple('BirchBark', (0.55, 0.55, 0.52), 0.8)
forestfloor_m = mat_simple('ForestFloor', (0.02, 0.035, 0.02), 0.98)

# ---------- far forest floor (covers horizon gap) ----------
bpy.ops.mesh.primitive_plane_add(size=240, location=(0, 60, -0.12))
fg = bpy.context.object; fg.name = 'FarGround'
fg.data.materials.append(forestfloor_m)
move_to_col(fg, bg_col)

# ---------- grass strip: low green mound at carpet/grass boundary ----------
bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=14, size=1)
gs = bpy.context.object; gs.name = 'GrassStrip'
gs.scale = (70, 9, 1)
gs.location = (0, 20, 0.02)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
tex = bpy.data.textures.get('grass_und') or bpy.data.textures.new('grass_und', 'CLOUDS')
tex.noise_scale = 0.9
d = gs.modifiers.new('mound', 'DISPLACE')
d.texture = tex; d.strength = 0.35; d.texture_coords = 'GLOBAL'
gs.data.materials.append(grass_m)
move_to_col(gs, mid_col)

# ---------- conifer mesh via bmesh (trunk + 3 cone tiers) ----------
def conifer_mesh(name):
    bm = bmesh.new()
    def cone(r1, r2, depth, z, seg=7):
        res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False,
                                    segments=seg, radius1=r1, radius2=r2, depth=depth)
        bmesh.ops.translate(bm, verts=res['verts'], vec=(0, 0, z))
    cone(0.14, 0.11, 1.4, 0.7)      # trunk
    cone(1.7, 0.6, 2.6, 2.4)        # bottom tier
    cone(1.25, 0.45, 2.2, 4.0)      # mid tier
    cone(0.75, 0.0, 2.0, 5.4)       # top tier
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(conifer_m)
    return me

cmesh = conifer_mesh('conifer_mesh')
# three depth rows of conifers
rows = [(30, 14, (0.9, 1.5)), (42, 18, (1.1, 1.9)), (55, 22, (1.3, 2.3))]
for y, half, (s0, s1) in rows:
    x = -half * 3.4
    while x < half * 3.4:
        x += random.uniform(2.2, 4.2)
        o = bpy.data.objects.new('conifer', cmesh)
        o.location = (x + random.uniform(-1, 1), y + random.uniform(-3, 3), 0)
        s = random.uniform(s0, s1)
        o.scale = (s, s, s * random.uniform(0.9, 1.3))
        o.rotation_euler.z = random.uniform(0, math.pi)
        bg_col.objects.link(o)

# ---------- distant mountains: jagged ridge mesh ----------
def ridge(name, y, h, w, seed):
    rnd = random.Random(seed)
    n = 14
    verts = [( -w/2 + w*i/(n-1), 0, rnd.uniform(h*0.4, h)) for i in range(n)]
    verts = [(-w/2, 0, 0)] + verts + [(w/2, 0, 0)]
    faces = [tuple(range(len(verts)))]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new(name, me)
    o.location = (0, y, 0)
    me.materials.append(sil_m)
    sol = o.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 2
    bg_col.objects.link(o)
    return o

ridge('mtn_far', 95, 9, 160, 3)
ridge('mtn_near', 78, 6, 140, 8)

# ---------- temple silhouette: stacked roofs (left distance) ----------
def roof_box(name, w, d, z, h=0.7):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z))
    b = bpy.context.object; b.name = name
    b.scale = (w/2, d/2, h/2)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=w*0.78, radius2=0.01,
                                    depth=h*0.9, location=(0, 0, z + h*0.55),
                                    rotation=(0, 0, math.radians(45)))
    r = bpy.context.object
    for uc in list(r.users_collection):
        uc.objects.unlink(r)
    for uc in list(b.users_collection):
        uc.objects.unlink(b)
    mid_col.objects.link(b); mid_col.objects.link(r)
    return b, r

def build_temple(base_loc):
    parts = []
    # body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.2))
    body = bpy.context.object; body.scale = (3.2, 2.2, 2.2)
    bpy.ops.object.transform_apply(scale=True)
    parts.append(body)
    for w, z in [(4.6, 4.4), (3.6, 6.3), (2.6, 8.0)]:
        b_, r_ = roof_box('rf', w, w*0.7, z)
        parts += [b_, r_]
    for p in parts:
        for uc in list(p.users_collection):
            uc.objects.unlink(p)
        mid_col.objects.link(p)
        p.data.materials.append(sil_m)
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    t = bpy.context.object; t.name = 'Temple'
    t.location = base_loc
    return t

build_temple((-17, 36, 0))

# ---------- stone lantern (right midground) ----------
def lantern(loc, s=1.0):
    parts = []
    def add(shape, **kw):
        nonlocal parts
        if shape == 'cube':
            bpy.ops.mesh.primitive_cube_add(size=1)
        elif shape == 'cyl':
            bpy.ops.mesh.primitive_cylinder_add(radius=kw.pop('r'), depth=kw.pop('d'), vertices=8)
        elif shape == 'cone':
            bpy.ops.mesh.primitive_cone_add(vertices=kw.pop('v', 4), radius1=kw.pop('r1'),
                                            radius2=kw.pop('r2'), depth=kw.pop('d'))
        o = bpy.context.object
        o.location = kw.get('loc', (0, 0, 0))
        if 'scale' in kw: o.scale = kw['scale']
        if 'rot' in kw: o.rotation_euler = kw['rot']
        parts.append(o)
    add('cube', loc=(0, 0, 0.15), scale=(0.7, 0.7, 0.3))       # base slab
    add('cyl', r=0.16, d=0.75, loc=(0, 0, 0.65))               # shaft
    add('cube', loc=(0, 0, 1.1), scale=(0.5, 0.5, 0.16))       # middle platform
    add('cube', loc=(0, 0, 1.38), scale=(0.34, 0.34, 0.4))     # fire box
    add('cone', v=4, r1=0.62, r2=0.12, d=0.36, loc=(0, 0, 1.78), rot=(0, 0, math.radians(45)))  # roof
    add('cyl', r=0.07, d=0.22, loc=(0, 0, 2.05))               # jewel
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        p.data.materials.append(stone_m)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    L = bpy.context.object; L.name = 'StoneLantern'
    L.scale = (s, s, s)
    L.location = loc
    move_to_col(L, mid_col)
    return L

lantern((6.3, 7.5, 0), 1.1)

# ---------- wooden post + small sign ----------
bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=1.6, location=(4.6, 6.6, 0.8))
post = bpy.context.object; post.name = 'WoodPost'
post.data.materials.append(wood_m)
move_to_col(post, mid_col)
bpy.ops.mesh.primitive_cube_add(size=1, location=(4.6, 6.6, 1.35), scale=(0.5, 0.05, 0.18))
sign = bpy.context.object; sign.name = 'WoodSign'
sign.data.materials.append(wood_m)
move_to_col(sign, mid_col)

# ---------- white birch at right edge ----------
def limb_cu(name, pts, mat, col_):
    cu = bpy.data.curves.new(name + '_cu', 'CURVE')
    cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 2
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, (co, r) in zip(sp.bezier_points, pts):
        bp.co = co; bp.radius = r
        bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu)
    col_.objects.link(o); o.data.materials.append(mat)
    return o

limb_cu('birch', [
    ((9.2, 3.5, -0.3), 0.14),
    ((9.1, 3.5, 1.8), 0.12),
    ((9.3, 3.6, 3.8), 0.095),
    ((9.0, 3.7, 5.8), 0.07),
    ((9.2, 3.7, 7.6), 0.05),
    ((8.9, 3.8, 9.2), 0.03),
], birch_m, mid_col)
for i, (a, b) in enumerate([
    ((9.15, 3.55, 4.2), (8.2, 3.4, 5.6)),
    ((9.1, 3.6, 6.0), (10.1, 3.5, 7.3)),
    ((9.05, 3.7, 7.4), (8.3, 3.6, 8.6)),
    ((9.0, 3.75, 8.2), (9.8, 3.7, 9.4)),
]):
    mid = ((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2 + 0.2)
    limb_cu(f'birch_br{i}', [(a, 0.03), (mid, 0.02), (b, 0.008)], birch_m, mid_col)

# small sparse leaf puffs on birch (reuse canopy GN)
can_col = col('CANOPY')
gn = bpy.data.node_groups['GN_Canopy']
bpuffs = []
for i, (c, r) in enumerate([((8.6, 3.5, 8.0), 0.9), ((9.6, 3.6, 9.0), 0.8), ((8.9, 3.7, 9.6), 0.7)]):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=1, location=c)
    p = bpy.context.object; p.scale.z = 0.7
    bpy.ops.object.transform_apply(scale=True)
    for uc in list(p.users_collection):
        uc.objects.unlink(p)
    can_col.objects.link(p)
    bpuffs.append(p)
bpy.ops.object.select_all(action='DESELECT')
for p in bpuffs:
    p.select_set(True)
bpy.context.view_layer.objects.active = bpuffs[0]
bpy.ops.object.join()
be = bpy.context.object; be.name = 'BirchEmitter'
m2 = be.modifiers.new('leafscatter', 'NODES'); m2.node_group = gn

# ---------- world fog: light blue volume ----------
w = scene.world
nt = w.node_tree
vol = nt.nodes.new('ShaderNodeVolumePrincipled')
vol.inputs['Density'].default_value = 0.009
vol.inputs['Color'].default_value = (0.55, 0.65, 0.8, 1)
vol.inputs['Anisotropy'].default_value = 0.15
out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputWorld')
nt.links.new(vol.outputs['Volume'], out.inputs['Volume'])

save()
render_preview('p05_background_eevee.png', pct=50)
