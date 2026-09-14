exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

random.seed(31)

# ---------- emitter mesh: 380 verts scattered in air box ----------
old = bpy.data.objects.get('FallEmitter')
if old:
    bpy.data.objects.remove(old, do_unlink=True)

verts = []
for _ in range(380):
    x = random.uniform(-9, 11)
    y = random.uniform(-10, 14)
    z = random.uniform(4.5, 10.0)
    verts.append((x, y, z))
me = bpy.data.meshes.new('FallEmitter_mesh')
me.from_pydata(verts, [], [])
em = bpy.data.objects.new('FallEmitter', me)
col('FALLING').objects.link(em)
em.display_type = 'WIRE'

# ---------- rewire GN: input points -> animated offset -> instance -> out ----------
ng = bpy.data.node_groups['GN_Falling']
dist = next((n for n in ng.nodes if n.bl_idname == 'GeometryNodeDistributePointsInVolume'), None)
if dist:
    ng.nodes.remove(dist)
inp = next(n for n in ng.nodes if n.bl_idname == 'NodeGroupInput')
outp = next(n for n in ng.nodes if n.bl_idname == 'NodeGroupOutput')
setpos = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeSetPosition')
inst = next(n for n in ng.nodes if n.bl_idname == 'GeometryNodeInstanceOnPoints')
for l in list(ng.links):
    if l.to_node == inp or (l.to_node == outp) or \
       (l.to_node == setpos and l.to_socket.name == 'Geometry') or \
       (l.to_node == inst and l.to_socket.name == 'Points'):
        ng.links.remove(l)
ng.links.new(inp.outputs['Geometry'], setpos.inputs['Geometry'])
ng.links.new(setpos.outputs['Geometry'], inst.inputs['Points'])
ng.links.new(inst.outputs['Instances'], outp.inputs['Geometry'])

mod = em.modifiers.new('falling', 'NODES')
mod.node_group = ng

save()
render_preview('p08d_fall_eevee.png', pct=50)
