exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

# ---------- cleanup old ground ----------
for o in list(bpy.data.objects):
    if o.name.startswith('PH_ground') or o.name == 'Ground':
        bpy.data.objects.remove(o, do_unlink=True)
gcol = col('GROUND')

# ---------- ground mesh 60x60, gentle undulation ----------
bpy.ops.mesh.primitive_grid_add(x_subdivisions=110, y_subdivisions=110, size=60)
ground = bpy.context.object
ground.name = 'Ground'
move_to_col(ground, gcol)
tex = bpy.data.textures.get('ground_und') or bpy.data.textures.new('ground_und', 'CLOUDS')
tex.noise_scale = 1.6
disp = ground.modifiers.new('undulate', 'DISPLACE')
disp.texture = tex
disp.strength = 0.22
disp.texture_coords = 'GLOBAL'

# ---------- litter material: dark red-brown, visible between leaves ----------
def litter_mat():
    m = bpy.data.materials.get('Litter') or bpy.data.materials.new('Litter')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 0.9
    noise.inputs['Detail'].default_value = 4.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].color = (0.045, 0.006, 0.004, 1)
    cr.elements[0].position = 0.2
    cr.elements[1].color = (0.22, 0.03, 0.012, 1)
    cr.elements[1].position = 0.85
    bsdf.inputs['Roughness'].default_value = 0.95
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

ground.data.materials.append(litter_mat())

# ---------- GN carpet: flat-ish leaves, denser near tree base ----------
def carpet_gn():
    ng = bpy.data.node_groups.get('GN_Carpet') or bpy.data.node_groups.new('GN_Carpet', 'GeometryNodeTree')
    ng.nodes.clear()
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    inp = ng.nodes.new('NodeGroupInput')
    outp = ng.nodes.new('NodeGroupOutput')

    join = ng.nodes.new('GeometryNodeJoinGeometry')
    ng.links.new(inp.outputs['Geometry'], join.inputs['Geometry'])

    dist = ng.nodes.new('GeometryNodeDistributePointsOnFaces')
    dist.distribute_method = 'POISSON'
    dist.inputs['Distance Min'].default_value = 0.06
    # density factor: near tree base (-4.6,0) -> high, far -> low
    pos = ng.nodes.new('GeometryNodeInputPosition')
    base = ng.nodes.new('FunctionNodeInputVector')
    base.vector = (-4.6, 0.0, 0.0)
    vdist = ng.nodes.new('ShaderNodeVectorMath')
    vdist.operation = 'DISTANCE'
    mpr = ng.nodes.new('ShaderNodeMapRange')
    mpr.inputs['From Min'].default_value = 2.0
    mpr.inputs['From Max'].default_value = 25.0
    mpr.inputs['To Min'].default_value = 240.0   # near: dense
    mpr.inputs['To Max'].default_value = 70.0    # far: sparse
    mpr.clamp = True
    ng.links.new(pos.outputs['Position'], vdist.inputs[0])
    ng.links.new(base.outputs['Vector'], vdist.inputs[1])
    ng.links.new(vdist.outputs['Value'], mpr.inputs['Value'])
    ng.links.new(mpr.outputs['Result'], dist.inputs['Density Max'])

    coll = ng.nodes.new('GeometryNodeCollectionInfo')
    coll.inputs['Collection'].default_value = bpy.data.collections['LEAF_SRC']
    coll.inputs['Separate Children'].default_value = True
    coll.inputs['Reset Children'].default_value = True
    inst = ng.nodes.new('GeometryNodeInstanceOnPoints')
    inst.inputs['Pick Instance'].default_value = True
    rnd_rot = ng.nodes.new('FunctionNodeRandomValue')
    rnd_rot.data_type = 'FLOAT_VECTOR'
    rnd_rot.inputs['Min'].default_value = (-0.38, -0.38, -math.pi)
    rnd_rot.inputs['Max'].default_value = (0.38, 0.38, math.pi)
    rnd_scl = ng.nodes.new('FunctionNodeRandomValue')
    rnd_scl.data_type = 'FLOAT'
    rnd_scl.inputs['Min'].default_value = 0.8
    rnd_scl.inputs['Max'].default_value = 1.5
    ng.links.new(dist.outputs['Points'], inst.inputs['Points'])
    ng.links.new(coll.outputs['Instances'], inst.inputs['Instance'])
    ng.links.new(rnd_rot.outputs['Value'], inst.inputs['Rotation'])
    ng.links.new(rnd_scl.outputs['Value'], inst.inputs['Scale'])

    # lift instances a touch along normal to avoid clipping
    setpos = ng.nodes.new('GeometryNodeSetPosition')
    nrm = ng.nodes.new('GeometryNodeInputNormal')
    vscale = ng.nodes.new('ShaderNodeVectorMath')
    vscale.operation = 'SCALE'
    vscale.inputs[3].default_value = 0.006
    ng.links.new(nrm.outputs['Normal'], vscale.inputs[0])
    ng.links.new(inst.outputs['Instances'], setpos.inputs['Geometry'])
    ng.links.new(vscale.outputs['Vector'], setpos.inputs['Offset'])

    ng.links.new(setpos.outputs['Geometry'], join.inputs['Geometry'])
    ng.links.new(join.outputs['Geometry'], outp.inputs['Geometry'])
    return ng

gn = carpet_gn()
mod = ground.modifiers.new('carpet', 'NODES')
mod.node_group = gn

save()
render_preview('p04_carpet_eevee.png', pct=50)
