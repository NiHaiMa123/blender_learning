exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene

# ---------- 1) stronger fog ----------
fm = bpy.data.materials['FogVol']
pv = next(n for n in fm.node_tree.nodes if n.bl_idname == 'ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value = 0.028

# ---------- 2) Nishita sky (sun glow right side) ----------
w = scene.world
nt = w.node_tree
bg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBackground')
sky = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexSky'), None)
if not sky:
    sky = nt.nodes.new('ShaderNodeTexSky')
sky.sky_type = 'MULTIPLE_SCATTERING'
for attr, val in [('sun_elevation', math.radians(14)),
                  ('sun_rotation', math.radians(115)),
                  ('altitude', 0.2),
                  ('air_density', 1.0),
                  ('dust_density', 1.2),
                  ('ozone_density', 1.0)]:
    try:
        setattr(sky, attr, val)
    except Exception as e:
        print('sky attr', attr, 'fail:', e)
nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 0.9

# ---------- 3) carpet stops at y<17; grass band widens ----------
ng = bpy.data.node_groups['GN_CarpetScatter']
dist = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces')
if not any(l.to_node == dist and l.to_socket.name == 'Selection' for l in ng.links):
    pos = ng.nodes.new('GeometryNodeInputPosition')
    sep = ng.nodes.new('ShaderNodeSeparateXYZ')
    cmpn = ng.nodes.new('FunctionNodeCompare')
    cmpn.operation = 'LESS_THAN'
    cmpn.data_type = 'FLOAT'
    cmpn.inputs[1].default_value = 17.0
    ng.links.new(pos.outputs['Position'], sep.inputs['Vector'])
    ng.links.new(sep.outputs['Y'], cmpn.inputs[0])
    ng.links.new(cmpn.outputs['Result'], dist.inputs['Selection'])

gs = bpy.data.objects.get('GrassStrip')
if gs:
    gs.scale = (90, 14, 1.6)
    gs.location = (0, 22, 0.02)
bpy.context.view_layer.objects.active = gs
gs.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
gs.select_set(False)
gm = bpy.data.materials['Grass']
gb = next(n for n in gm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
gb.inputs['Base Color'].default_value = (0.07, 0.16, 0.03, 1)

# ---------- 4) push front conifer row back a bit ----------
for o in bpy.data.collections['BACKGROUND'].objects:
    if o.name.startswith('conifer') and 25 < o.location.y < 36:
        o.location.y += 6

# ---------- 5) sun a bit warmer/stronger ----------
sun = bpy.data.objects.get('Sun')
if sun:
    sun.data.energy = 5.0
    sun.data.color = (1.0, 0.82, 0.62)

save()
render_preview('p06_atmo_eevee.png', pct=50)
