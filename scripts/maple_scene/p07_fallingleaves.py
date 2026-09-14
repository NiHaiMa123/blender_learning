exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene
scene.render.fps = 24

# ---------- falling leaf emitter: air volume in view corridor ----------
old = bpy.data.objects.get('FallEmitter')
if old:
    bpy.data.objects.remove(old, do_unlink=True)

# box covering the airspace the camera sees: x -9..11, y -10..14, z 0.5..10
bpy.ops.mesh.primitive_cube_add(size=2)
em = bpy.context.object
em.name = 'FallEmitter'
em.location = (1, 2, 5.2)
em.scale = (10, 12, 4.8)
em.display_type = 'WIRE'
move_to_col(em, col('FALLING'))

ng = bpy.data.node_groups.get('GN_Falling')
if ng:
    bpy.data.node_groups.remove(ng)
ng = bpy.data.node_groups.new('GN_Falling', 'GeometryNodeTree')
ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
inp = ng.nodes.new('NodeGroupInput')
outp = ng.nodes.new('NodeGroupOutput')

dist = ng.nodes.new('GeometryNodeDistributePointsInVolume')
dist.inputs['Density'].default_value = 0.09
ng.links.new(inp.outputs['Geometry'], dist.inputs['Volume'])

# --- animation: z = top - wrap(seconds*speed + rand*H, 0, H); x sway sin ---
st = ng.nodes.new('GeometryNodeInputSceneTime')
rnd_speed = ng.nodes.new('FunctionNodeRandomValue')
rnd_speed.data_type = 'FLOAT'
rnd_speed.inputs['Min'].default_value = 0.35
rnd_speed.inputs['Max'].default_value = 0.9
rnd_phase = ng.nodes.new('FunctionNodeRandomValue')
rnd_phase.data_type = 'FLOAT'
rnd_phase.inputs['Min'].default_value = 0.0
rnd_phase.inputs['Max'].default_value = 9.6     # height H
mul = ng.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
add = ng.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
wrap = ng.nodes.new('ShaderNodeMath'); wrap.operation = 'WRAP'
wrap.inputs[1].default_value = 0.0
wrap.inputs[2].default_value = 9.6
sub = ng.nodes.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'
sub.inputs[0].default_value = 0.0               # offset = -wrapped
ng.links.new(st.outputs['Seconds'], mul.inputs[0])
ng.links.new(rnd_speed.outputs['Value'], mul.inputs[1])
ng.links.new(mul.outputs['Value'], add.inputs[0])
ng.links.new(rnd_phase.outputs['Value'], add.inputs[1])
ng.links.new(add.outputs['Value'], wrap.inputs[0])
ng.links.new(wrap.outputs['Value'], sub.inputs[1])

sway_m = ng.nodes.new('ShaderNodeMath'); sway_m.operation = 'MULTIPLY'
sway_m.inputs[1].default_value = 0.6
sway_ph = ng.nodes.new('ShaderNodeMath'); sway_ph.operation = 'MULTIPLY'
sway_ph.inputs[1].default_value = 6.283
sway_add = ng.nodes.new('ShaderNodeMath'); sway_add.operation = 'ADD'
sway_sin = ng.nodes.new('ShaderNodeMath'); sway_sin.operation = 'SINE'
sway_amp = ng.nodes.new('ShaderNodeMath'); sway_amp.operation = 'MULTIPLY'
sway_amp.inputs[1].default_value = 0.5
ng.links.new(st.outputs['Seconds'], sway_m.inputs[0])
ng.links.new(rnd_phase.outputs['Value'], sway_ph.inputs[0])
ng.links.new(sway_m.outputs['Value'], sway_add.inputs[0])
ng.links.new(sway_ph.outputs['Value'], sway_add.inputs[1])
ng.links.new(sway_add.outputs['Value'], sway_sin.inputs[0])
ng.links.new(sway_sin.outputs['Value'], sway_amp.inputs[0])

comb = ng.nodes.new('ShaderNodeCombineXYZ')
ng.links.new(sway_amp.outputs['Value'], comb.inputs['X'])
ng.links.new(sub.outputs['Value'], comb.inputs['Z'])
setpos = ng.nodes.new('GeometryNodeSetPosition')
ng.links.new(dist.outputs['Points'], setpos.inputs['Geometry'])
ng.links.new(comb.outputs['Vector'], setpos.inputs['Offset'])

coll = ng.nodes.new('GeometryNodeCollectionInfo')
coll.inputs['Collection'].default_value = bpy.data.collections['LEAF_SRC']
coll.inputs['Separate Children'].default_value = True
coll.inputs['Reset Children'].default_value = True
inst = ng.nodes.new('GeometryNodeInstanceOnPoints')
inst.inputs['Pick Instance'].default_value = True
rot = ng.nodes.new('FunctionNodeRandomValue')
rot.data_type = 'FLOAT_VECTOR'
rot.inputs['Min'].default_value = (-math.pi, -math.pi, -math.pi)
rot.inputs['Max'].default_value = (math.pi, math.pi, math.pi)
scl = ng.nodes.new('FunctionNodeRandomValue')
scl.data_type = 'FLOAT'
scl.inputs['Min'].default_value = 0.8
scl.inputs['Max'].default_value = 1.4
ng.links.new(setpos.outputs['Geometry'], inst.inputs['Points'])
ng.links.new(coll.outputs['Instances'], inst.inputs['Instance'])
ng.links.new(rot.outputs['Value'], inst.inputs['Rotation'])
ng.links.new(scl.outputs['Value'], inst.inputs['Scale'])
ng.links.new(inst.outputs['Instances'], outp.inputs['Geometry'])

mod = em.modifiers.new('falling', 'NODES')
mod.node_group = ng

# ---------- polish tweaks ----------
# trunk: lighten bark a touch
bm = bpy.data.materials['Bark']
ramp = next(n for n in bm.node_tree.nodes if n.bl_idname == 'ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.015, 0.006, 0.004, 1)
ramp.color_ramp.elements[1].color = (0.075, 0.035, 0.02, 1)

# sky: more saturated
bg = next(n for n in scene.world.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.06, 0.26, 0.85, 1)
bg.inputs['Strength'].default_value = 0.75

# fog: a touch thinner so front row reads greener
pv = next(n for n in bpy.data.materials['FogVol'].node_tree.nodes
          if n.bl_idname == 'ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.028

# grass: more saturated
grm = bpy.data.materials['Grass']
gb = next(n for n in grm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
gb.inputs['Base Color'].default_value = (0.06, 0.18, 0.025, 1)

# small sapling mid-left for depth (reuse bark+leaf assets via curve+emitter)
tree_col = col('TREE')
can_col = col('CANOPY')
cu = bpy.data.curves.new('sapling_cu', 'CURVE')
cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 2
sp = cu.splines.new('BEZIER')
pts = [((-7.6, 2.5, -0.2), 0.10), ((-7.7, 2.5, 1.4), 0.08),
       ((-7.5, 2.6, 2.8), 0.055), ((-7.3, 2.6, 4.1), 0.03)]
sp.bezier_points.add(len(pts) - 1)
for bp, (co, r) in zip(sp.bezier_points, pts):
    bp.co = co; bp.radius = r
    bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
sap = bpy.data.objects.new('Sapling', cu)
tree_col.objects.link(sap)
sap.data.materials.append(bm)

gn = bpy.data.node_groups['GN_Canopy']
spuffs = []
for c, r in [((-7.5, 2.6, 4.4), 0.85), ((-7.9, 2.5, 3.8), 0.6), ((-7.2, 2.6, 5.0), 0.65)]:
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=1, location=c)
    p = bpy.context.object; p.scale.z = 0.75
    bpy.ops.object.transform_apply(scale=True)
    for uc in list(p.users_collection):
        uc.objects.unlink(p)
    can_col.objects.link(p)
    spuffs.append(p)
bpy.ops.object.select_all(action='DESELECT')
for p in spuffs:
    p.select_set(True)
bpy.context.view_layer.objects.active = spuffs[0]
bpy.ops.object.join()
se = bpy.context.object; se.name = 'SaplingEmitter'
m2 = se.modifiers.new('leafscatter', 'NODES'); m2.node_group = gn

# subtle DOF: focus on trunk, f/4
cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = True
cam.data.dof.focus_object = bpy.data.objects.get('MapleTree')
cam.data.dof.aperture_fstop = 5.0

save()
render_preview('p07_falling_eevee.png', pct=50)
scene.cycles.samples = 64
render_preview('p07_falling_cycles.png', engine='CYCLES', pct=50)
