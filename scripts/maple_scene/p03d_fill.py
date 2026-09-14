exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

can_col = col('CANOPY')
emitter = bpy.data.objects.get('CanopyEmitter')

# extra fill puffs -> join into existing emitter
extra = [
    # connect right extension chain
    ((6.6, 0.7, 8.6), 1.3, 0.7),
    ((7.6, 0.7, 8.8), 1.2, 0.7),
    ((8.5, 0.7, 9.0), 1.1, 0.7),
    # smooth scalloped bottom edge (medium fill between balls)
    ((-4.6, 0.35, 8.0), 1.0, 0.65),
    ((-3.6, 0.3, 7.3), 0.9, 0.65),
    ((-2.0, 0.4, 7.3), 0.95, 0.65),
    ((-0.2, 0.5, 7.4), 1.0, 0.65),
    ((1.5, 0.6, 7.6), 0.95, 0.65),
    ((3.2, 0.6, 7.8), 0.9, 0.65),
    ((4.7, 0.65, 7.9), 0.85, 0.65),
    # left fork cover + lower-left foliage to frame edge
    ((-4.3, 0.1, 6.4), 0.95, 0.7),
    ((-5.4, 0.2, 7.0), 1.0, 0.7),
    ((-6.9, 0.45, 7.9), 1.0, 0.75),
    # top frame-fill row
    ((-7.8, 0.6, 10.4), 1.4, 0.85),
    ((-5.5, 0.7, 10.3), 1.5, 0.85),
    ((-3.0, 0.8, 10.0), 1.5, 0.8),
    ((-0.5, 0.9, 10.2), 1.5, 0.8),
    ((2.0, 0.9, 10.3), 1.4, 0.8),
    ((4.6, 0.9, 10.2), 1.4, 0.8),
    ((6.9, 0.9, 10.0), 1.3, 0.8),
]
puffs = []
for i, (c, r, sz) in enumerate(extra):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=2, location=c)
    p = bpy.context.object
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
emitter.select_set(True)
bpy.context.view_layer.objects.active = emitter
bpy.ops.object.join()  # joins puffs into emitter (keeps its GN modifier)

save()
render_preview('p03d_canopy_eevee.png', pct=50)
