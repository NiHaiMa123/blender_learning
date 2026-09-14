"""Phase 10c: real maple leaf CARDS — V-fold cards UV'd to per-leaf bboxes
of LeafSet021 atlas (component analysis), alpha-clip silhouette.
Studio isolation renders: lineup, single closeup, cluster."""
import bpy, math, os, sys
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, move_to_col, save, RENDER_DIR

TEX = r'C:/Users/Administrator/AppData/Local/Temp/leafref/LeafSet021'
IMG_COLOR = os.path.join(TEX, 'LeafSet021_1K-JPG_Color.jpg')
IMG_OPAC = os.path.join(TEX, 'LeafSet021_1K-JPG_Opacity.jpg')
IMG_NORM = os.path.join(TEX, 'LeafSet021_1K-JPG_NormalGL.jpg')
IMG_ROUGH = os.path.join(TEX, 'LeafSet021_1K-JPG_Roughness.jpg')
STUDIO = 'LEAF_STUDIO'

# leaf bboxes from component analysis (pixel coords, y from bottom)
LEAVES = [
    (773, 271, 979, 507),   # biggest, bottom-right
    (783,   8, 959, 243),   # top-right
    (513,   8, 691, 238),   # top-middle-right
]
W, H = 1024, 512
FOLD = math.radians(20)

# ---------------- material: photo + alpha + normal + rough ----------------
m = bpy.data.materials.get('MapleLeaf2') or bpy.data.materials.new('MapleLeaf2')
m.use_nodes = True
nt = m.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
if bsdf.inputs.get('Emission Strength'):
    bsdf.inputs['Emission Strength'].default_value = 0.25
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(IMG_COLOR)
hue = nt.nodes.new('ShaderNodeHueSaturation')
hue.inputs['Hue'].default_value = 0.30
hue.inputs['Saturation'].default_value = 1.2
hue.inputs['Value'].default_value = 1.1
op = nt.nodes.new('ShaderNodeTexImage'); op.image = bpy.data.images.load(IMG_OPAC)
op.image.colorspace_settings.name = 'Non-Color'
ntex = nt.nodes.new('ShaderNodeTexImage'); ntex.image = bpy.data.images.load(IMG_NORM)
ntex.image.colorspace_settings.name = 'Non-Color'
nmap = nt.nodes.new('ShaderNodeNormalMap'); nmap.inputs['Strength'].default_value = 0.7
rtex = nt.nodes.new('ShaderNodeTexImage'); rtex.image = bpy.data.images.load(IMG_ROUGH)
rtex.image.colorspace_settings.name = 'Non-Color'
oi = nt.nodes.new('ShaderNodeObjectInfo')
mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs['To Min'].default_value = 0.9
mr.inputs['To Max'].default_value = 1.15
nt.links.new(tex.outputs['Color'], hue.inputs['Color'])
nt.links.new(oi.outputs['Random'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], hue.inputs['Value'])
nt.links.new(hue.outputs['Color'], bsdf.inputs['Base Color'])
if bsdf.inputs.get('Emission Color'):
    nt.links.new(hue.outputs['Color'], bsdf.inputs['Emission Color'])
nt.links.new(op.outputs['Color'], bsdf.inputs['Alpha'])
nt.links.new(ntex.outputs['Color'], nmap.inputs['Color'])
nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
nt.links.new(rtex.outputs['Color'], bsdf.inputs['Roughness'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
try:
    m.surface_render_method = 'DITHERED'
except Exception:
    try:
        m.blend_method = 'CLIP'
    except Exception:
        pass

# ---------------- V-fold card per leaf bbox ----------------
def make_card(name, box):
    x0, y0, x1, y1 = box
    pad = 2
    u0, v0 = (x0 - pad) / W, (y0 - pad) / H
    u1, v1 = (x1 + pad) / W, (y1 + pad) / H
    um = (u0 + u1) / 2
    ar = (x1 - x0) / (y1 - y0)              # width/height
    w, h = 0.25 * ar, 0.25                  # 25cm tall card
    fy = (w / 2) * math.tan(FOLD)
    verts = [(-w/2, fy,  h/2), (-w/2, fy, -h/2),
             (0,    0,   h/2), (0,    0,  -h/2),
             (w/2,  fy,  h/2), (w/2,  fy, -h/2)]
    faces = [(0, 1, 3, 2), (2, 3, 5, 4)]
    me = bpy.data.meshes.new(name + 'Mesh')
    me.from_pydata(verts, [], faces); me.update()
    uvl = me.uv_layers.new(name='UVMap')
    uv_map = {0: (u0, v1), 1: (u0, v0), 2: (um, v1), 3: (um, v0),
              4: (u1, v1), 5: (u1, v0)}
    for i, loop in enumerate(me.loops):
        uvl.data[i].uv = uv_map[loop.vertex_index]
    old = bpy.data.objects.get(name)
    if old:
        old.data = me
        ob = old
    else:
        ob = bpy.data.objects.new(name, me)
        col(STUDIO).objects.link(ob)
    if not len(me.materials):
        me.materials.append(m)
    return ob

# clear broken traced leaves
for n in ['RealLeaf_0', 'RealLeaf_1', 'RealLeaf_2']:
    o = bpy.data.objects.get(n)
    if o:
        o.hide_render = True

leaf_obs = []
for i, box in enumerate(LEAVES):
    ob = make_card(f'LeafCard_{i}', box)
    ob.location = (i * 0.35 - 0.35, 0, 0)
    ob.rotation_euler = (0, 0, 0)
    ob.hide_render = False
    leaf_obs.append(ob)

# cluster: ring of 5 cards around a point (twig spray)
for i in range(5):
    src = leaf_obs[i % 3]
    c = bpy.data.objects.get(f'Clu_{i}') or src.copy()
    c.data = src.data
    c.name = f'Clu_{i}'
    if not c.users_collection:
        col(STUDIO).objects.link(c)
    a = math.radians(-70 + 35 * i)
    c.rotation_euler = (math.radians(10 + 8 * i), math.radians(5 * (i - 2)), a)
    c.location = (0.9, 0.02 * i, -0.02 * abs(i - 2))
    c.hide_render = True

twig = bpy.data.objects.get('ClusterTwig')
if twig:
    twig.location = (0.9, 0, -0.14)
    twig.hide_render = True

# ---------------- fix lighting ----------------
sun = bpy.data.objects.get('StudioSun')
if sun:
    sun.data.energy = 4.0
    sun.rotation_euler = (math.radians(120), 0, 0)   # from behind leaf (+Y side)
area = bpy.data.objects.get('StudioArea')
if area:
    area.data.energy = 800
    area.data.size = 0.8
    area.location = (0.2, -1.2, 0.5)
    area.rotation_euler = (math.radians(70), 0, 0)
# second soft fill from below-front
fill = bpy.data.objects.get('StudioFill')
if not fill:
    fill = bpy.data.objects.new('StudioFill', bpy.data.lights.new('StudioFill', 'AREA'))
    col(STUDIO).objects.link(fill)
fill.data.energy = 200
fill.data.size = 1.0
fill.location = (-0.4, -0.8, -0.5)
fill.rotation_euler = (math.radians(120), 0, 0)

# world slightly brighter
w = bpy.context.scene.world
for n in w.node_tree.nodes:
    if n.bl_idname == 'ShaderNodeBackground':
        n.inputs['Color'].default_value = (0.04, 0.05, 0.07, 1)
        n.inputs['Strength'].default_value = 0.5

cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = False
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100
try:
    s.cycles.samples = 64
except Exception:
    pass

# 1) lineup
cam.data.lens = 45
cam.location = (0, -1.4, 0)
cam.rotation_euler = (math.radians(90), 0, 0)
s.render.filepath = os.path.join(RENDER_DIR, 'p10c_lineup.png')
bpy.ops.render.render(write_still=True)
print('RENDERED lineup')

# 2) single closeup
for o in leaf_obs[1:]:
    o.hide_render = True
leaf_obs[0].location = (0, 0, 0)
cam.data.lens = 70
cam.location = (0, -0.75, 0.02)
s.render.filepath = os.path.join(RENDER_DIR, 'p10c_single.png')
bpy.ops.render.render(write_still=True)
print('RENDERED single')

# 3) cluster
leaf_obs[0].hide_render = True
for i in range(5):
    bpy.data.objects[f'Clu_{i}'].hide_render = False
if twig:
    twig.hide_render = False
cam.data.lens = 50
cam.location = (0.9, -1.1, 0.05)
s.render.filepath = os.path.join(RENDER_DIR, 'p10c_cluster.png')
bpy.ops.render.render(write_still=True)
print('RENDERED cluster')

save()
print('P10C DONE')
