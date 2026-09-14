exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

# ============ maple leaf material ============
def make_leaf_material():
    m = bpy.data.materials.get('MapleLeaf') or bpy.data.materials.new('MapleLeaf')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    mix = nt.nodes.new('ShaderNodeMixShader')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    transl = nt.nodes.new('ShaderNodeBsdfTranslucent')
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp2 = nt.nodes.new('ShaderNodeValToRGB')

    # deep crimson -> red -> orange -> amber
    cr = ramp.color_ramp
    cr.elements.remove(cr.elements[1])
    e0 = cr.elements[0]; e0.position = 0.0; e0.color = (0.16, 0.004, 0.008, 1)
    for pos, c in [(0.35, (0.42, 0.015, 0.01, 1)),
                   (0.62, (0.72, 0.09, 0.015, 1)),
                   (0.85, (0.85, 0.22, 0.03, 1)),
                   (1.0, (0.95, 0.4, 0.06, 1))]:
        e = cr.elements.new(pos); e.color = c

    cr2 = ramp2.color_ramp
    cr2.elements.remove(cr2.elements[1])
    e0 = cr2.elements[0]; e0.position = 0.0; e0.color = (0.5, 0.02, 0.02, 1)
    e1 = cr2.elements.new(1.0); e1.color = (1.0, 0.25, 0.05, 1)

    bsdf.inputs['Roughness'].default_value = 0.55
    mix.inputs[0].default_value = 0.38  # translucent fraction

    nt.links.new(oi.outputs['Random'], ramp.inputs['Fac'])
    nt.links.new(oi.outputs['Random'], ramp2.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(ramp2.outputs['Color'], transl.inputs['Color'])
    nt.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
    nt.links.new(transl.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return m

# ============ single leaf mesh ============
def build_leaf(name, n_lobes=7, depth=0.62, sharp=0.65, serr=0.05,
               serr_freq=34, n_pts=180, R=0.065, phase=0.0, droop=0.10):
    # polar outline: deep palmate sinuses + serrated edge
    us = []
    for i in range(n_pts):
        t = 2 * math.pi * i / n_pts
        u = 1 - depth * abs(math.sin(n_lobes * t / 2 + phase)) ** sharp
        u *= 1 + serr * math.sin(serr_freq * t + phase * 3)
        us.append(u)

    verts = [(0.0, 0.0, 0.004)]  # center
    # inner ring (45% radius)
    for i in range(n_pts):
        t = 2 * math.pi * i / n_pts
        u = us[i] * 0.45
        verts.append((R * u * math.cos(t), R * u * math.sin(t), 0.002))
    # outer ring, tips droop slightly downward (-Z)
    for i in range(n_pts):
        t = 2 * math.pi * i / n_pts
        u = us[i]
        z = -droop * R * u * u
        verts.append((R * u * math.cos(t), R * u * math.sin(t), z))

    faces = []
    # center fan: center(0) -> inner ring 1..n_pts
    for i in range(n_pts):
        a = 1 + i
        b = 1 + (i + 1) % n_pts
        faces.append((0, a, b))
    # ring quads: inner(1..n) -> outer(n+1..2n)
    for i in range(n_pts):
        a = 1 + i
        b = 1 + (i + 1) % n_pts
        c = 1 + n_pts + (i + 1) % n_pts
        d = 1 + n_pts + i
        faces.append((a, d, c, b))

    me = bpy.data.meshes.new(name + '_mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)

    # petiole: thin tapered cylinder at bottom notch
    # bottom notch direction: t where lobe gap at -Y => t=3pi/2
    base = Vector((0.0, -depth * R * 0.9, -droop * R * 0.14))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0009, depth=0.035,
                                        location=(0, 0, 0))
    pet = bpy.context.object
    # orient cylinder along Y, attach at base
    pet.rotation_euler = (math.radians(90), 0, 0)
    pet.location = base + Vector((0, -0.014, 0.002))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    pet.name = name + '_petiole'

    # join petiole into leaf
    src = col('LEAF_SRC')
    src.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True); pet.select_set(True)
    bpy.ops.object.join()
    obj.select_set(False)

    # single clean material slot; join can leave an empty slot at index 0
    obj.data.materials.clear()
    obj.data.materials.append(bpy.data.materials['MapleLeaf'])
    for p in obj.data.polygons:
        p.material_index = 0
        p.use_smooth = True
    sol = obj.modifiers.new('thick', 'SOLIDIFY')
    sol.thickness = 0.0006
    return obj

# ============ build 3 variants ============
mat = make_leaf_material()
# ensure LEAF_SRC is in the view layer while we build (select/join needs it)
_lc = bpy.context.view_layer.layer_collection.children.get('LEAF_SRC')
if _lc:
    _lc.exclude = False
src = col('LEAF_SRC')
for o in list(src.objects):
    bpy.data.objects.remove(o, do_unlink=True)

variants = [
    ('leaf_A', dict(n_lobes=7, depth=0.60, sharp=0.62, serr=0.045, phase=-1.75 * math.pi)),
    ('leaf_B', dict(n_lobes=7, depth=0.68, sharp=0.55, serr=0.06, serr_freq=30, phase=-1.75 * math.pi + 0.35)),
    ('leaf_C', dict(n_lobes=5, depth=0.55, sharp=0.7, serr=0.05, serr_freq=40, phase=-2.5 * math.pi)),
]
leaves = []
for name, kw in variants:
    o = build_leaf(name, **kw)
    leaves.append(o)
    print('built', name, 'verts', len(o.data.vertices))

# hide source collection from render (instances still work)
def hide_col(name):
    lc = bpy.context.view_layer.layer_collection.children.get(name)
    if lc:
        lc.exclude = True
hide_col('LEAF_SRC')

# ============ backlit material test ============
test = col('LEAF_TEST')
for o in list(test.objects):
    bpy.data.objects.remove(o, do_unlink=True)

import random as _r
_r.seed(7)
for i, src_obj in enumerate(leaves):
    for j in range(2):
        d = src_obj.copy()  # linked mesh, gets own random -> color variation
        d.location = (0.5 + (i - 1) * 0.18, -11.6 + j * 0.12, 1.05 + j * 0.05)
        d.rotation_euler = (math.radians(75 + _r.uniform(-15, 15)),
                            _r.uniform(-0.3, 0.3),
                            _r.uniform(0, math.pi))
        test.objects.link(d)

save()
bpy.context.scene.cycles.samples = 48
render_preview('p02_leaf_test_eevee.png', pct=60)
render_preview('p02_leaf_test_cycles.png', engine='CYCLES', pct=40)
