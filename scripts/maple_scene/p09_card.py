"""Phase 9 test: photo leaf-card canopy (asset technique from lakeside scene).
Creates CardLeaf quad + MapleCard material, scatters via GN_CardCanopy on
CanopyEmitter, disables procedural leafscatter for A/B comparison."""
import bpy, os, sys
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, move_to_col, save, render_preview

TEX = r'D:/project/blender_learning/scripts/asset_tex'
DIFFUSE = os.path.join(TEX, 'cgaxis_tree_15_02_jpg_001.jpg')
OPACITY = os.path.join(TEX, 'cgaxis_tree_15_02_opacity_jpg_001.jpg')

# ---------- 1. card mesh (quad, portrait aspect matching 461x700) ----------
me = bpy.data.meshes.get('CardLeafMesh') or bpy.data.meshes.new('CardLeafMesh')
if not me.vertices:
    w, h = 0.66, 1.0
    verts = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name='UVMap')
    for i, loop in enumerate(me.loops):
        uvl.data[i].uv = (verts[loop.vertex_index][0] / w + 0.5,
                          verts[loop.vertex_index][2] / h + 0.5)
    me.update()

card = bpy.data.objects.get('CardLeaf') or bpy.data.objects.new('CardLeaf', me)
if not card.users_collection:
    col('LEAF_SRC').objects.link(card)

# ---------- 2. material: photo -> hue shift to red -> base+emission ----------
m = bpy.data.materials.get('MapleCard') or bpy.data.materials.new('MapleCard')
m.use_nodes = True
nt = m.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (600, 0)
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 0)
bsdf.inputs['Roughness'].default_value = 0.55
if bsdf.inputs.get('Specular IOR Level'):
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
if bsdf.inputs.get('Emission Strength'):
    bsdf.inputs['Emission Strength'].default_value = 0.3

tex = nt.nodes.new('ShaderNodeTexImage'); tex.location = (-600, 100)
tex.image = bpy.data.images.load(DIFFUSE)
op = nt.nodes.new('ShaderNodeTexImage'); op.location = (-600, -200)
op.image = bpy.data.images.load(OPACITY)
op.image.colorspace_settings.name = 'Non-Color'

hue = nt.nodes.new('ShaderNodeHueSaturation'); hue.location = (-350, 100)
hue.inputs['Hue'].default_value = 0.15          # green -> red shift
hue.inputs['Saturation'].default_value = 1.25
hue.inputs['Value'].default_value = 1.0
bc = nt.nodes.new('ShaderNodeBrightContrast'); bc.location = (-100, 100)
bc.inputs['Contrast'].default_value = 0.1

oi = nt.nodes.new('ShaderNodeObjectInfo'); oi.location = (-600, 350)
mr = nt.nodes.new('ShaderNodeMapRange'); mr.location = (-350, 350)
mr.inputs['From Min'].default_value = 0.0
mr.inputs['From Max'].default_value = 1.0
mr.inputs['To Min'].default_value = 0.8          # per-instance brightness
mr.inputs['To Max'].default_value = 1.2

nt.links.new(tex.outputs['Color'], hue.inputs['Color'])
nt.links.new(hue.outputs['Color'], bc.inputs['Color'])
nt.links.new(bc.outputs['Color'], bsdf.inputs['Base Color'])
if bsdf.inputs.get('Emission Color'):
    nt.links.new(bc.outputs['Color'], bsdf.inputs['Emission Color'])
nt.links.new(op.outputs['Color'], bsdf.inputs['Alpha'])
nt.links.new(oi.outputs['Random'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], hue.inputs['Value'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

try:
    m.surface_render_method = 'DITHERED'
except Exception:
    try:
        m.blend_method = 'CLIP'
    except Exception:
        pass

if me.materials:
    me.materials[0] = m
else:
    me.materials.append(m)

# ---------- 3. GN group: scatter card instances on emitter faces ----------
g = bpy.data.node_groups.get('GN_CardCanopy') or bpy.data.node_groups.new('GN_CardCanopy', 'GeometryNodeTree')
g.interface.clear()
g.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
g.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
g.nodes.clear()
ni = g.nodes.new('NodeGroupInput'); ni.location = (-500, 0)
no = g.nodes.new('NodeGroupOutput'); no.location = (500, 0)

dp = g.nodes.new('GeometryNodeDistributePointsOnFaces'); dp.location = (-250, 100)
dp.distribute_method = 'RANDOM'
if dp.inputs.get('Density Max'):
    dp.inputs['Density Max'].default_value = 6.0

ip = g.nodes.new('GeometryNodeInstanceOnPoints'); ip.location = (250, 0)
ip.inputs['Pick Instance'].default_value = False

goi = g.nodes.new('GeometryNodeObjectInfo'); goi.location = (-250, -200)
goi.transform_space = 'ORIGINAL'
goi.inputs['Object'].default_value = card
if goi.inputs.get('As Instance'):
    goi.inputs['As Instance'].default_value = True

rv = g.nodes.new('FunctionNodeRandomValue'); rv.data_type = 'FLOAT_VECTOR'; rv.location = (0, -350)
rv.inputs['Min'].default_value = (-3.1416, -3.1416, -3.1416)
rv.inputs['Max'].default_value = (3.1416, 3.1416, 3.1416)
rs = g.nodes.new('FunctionNodeRandomValue'); rs.data_type = 'FLOAT'; rs.location = (0, -500)
rs.inputs['Min'].default_value = 0.12
rs.inputs['Max'].default_value = 0.24

g.links.new(ni.outputs['Geometry'], dp.inputs['Mesh'])
g.links.new(dp.outputs['Points'], ip.inputs['Points'])
g.links.new(goi.outputs['Geometry'], ip.inputs['Instance'])
g.links.new(rv.outputs['Value'], ip.inputs['Rotation'])
g.links.new(rs.outputs['Value'], ip.inputs['Scale'])
g.links.new(ip.outputs['Instances'], no.inputs['Geometry'])

# ---------- 4. attach to CanopyEmitter, disable procedural leaves ----------
em = bpy.data.objects['CanopyEmitter']
old = em.modifiers.get('leafscatter')
if old:
    old.show_render = False
    old.show_viewport = False
mod = em.modifiers.get('cardscatter') or em.modifiers.new('cardscatter', 'NODES')
mod.node_group = g

save()
render_preview('p09_card_eevee.png', pct=50)
print('CARD TEST DONE')
