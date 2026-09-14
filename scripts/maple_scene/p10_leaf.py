"""Phase 10: real maple leaf assets from ambientCG LeafSet021 (CC0 photogrammetry).
- Trace true leaf silhouette from opacity map via polar raycast (star-shaped)
- Fan-triangulated mesh, UV-mapped to atlas cell, V-fold along midrib
- Materials: photo color (hue->red) + Normal + Roughness + emission translucency
- Isolated studio render: single leaf + 3-leaf cluster, rest of scene hidden
"""
import bpy, bmesh, math, os, sys
import numpy as np
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, move_to_col, save, RENDER_DIR

TEX = r'C:/Users/Administrator/AppData/Local/Temp/leafref/LeafSet021'
IMG_COLOR = os.path.join(TEX, 'LeafSet021_1K-JPG_Color.jpg')
IMG_OPAC = os.path.join(TEX, 'LeafSet021_1K-JPG_Opacity.jpg')
IMG_NORM = os.path.join(TEX, 'LeafSet021_1K-JPG_NormalGL.jpg')
IMG_ROUGH = os.path.join(TEX, 'LeafSet021_1K-JPG_Roughness.jpg')

STUDIO = 'LEAF_STUDIO'
NRAYS = 160
LEAF_H = 0.30            # meters tall
FOLD = 0.06              # V-fold depth ratio of width

# ---------------- load opacity pixels ----------------
op_img = bpy.data.images.load(IMG_OPAC)
op_img.update()
W, H = op_img.size
px = np.array(op_img.pixels[:], dtype=np.float32).reshape(H, W, 4)
mask = px[:, :, 0] > 0.5          # R channel of opacity jpg
print('opacity', W, H, 'coverage', mask.mean())

COLS, ROWS = 4, 2
def cell_mask(cx, cy):
    """mask for leaf in cell (cx=col 0..3, cy=row 0..1 top-down in UV space)"""
    x0, x1 = cx * W // COLS, (cx + 1) * W // COLS
    # image row 0 = bottom; leaf grid row 0 = top of image
    y0 = H - (cy + 1) * H // ROWS
    y1 = H - cy * H // ROWS
    return mask[y0:y1, x0:x1], x0, y0, x1, y1

def trace_leaf(cx, cy):
    """return outline verts in image pixel coords + centroid, for cell"""
    m, x0, y0, x1, y1 = cell_mask(cx, cy)
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    ccx, ccy = xs.mean(), ys.mean()
    ch, cw = m.shape
    outline = []
    for i in range(NRAYS):
        a = 2 * math.pi * i / NRAYS
        dx, dy = math.cos(a), math.sin(a)
        r, last = 0.0, 0.0
        while r < max(cw, ch) * 1.2:
            ix, iy = int(ccx + dx * r), int(ccy + dy * r)
            if ix < 0 or iy < 0 or ix >= cw or iy >= ch or not m[iy, ix]:
                break
            last = r
            r += 0.7
        outline.append((x0 + ccx + dx * last, y0 + ccy + dy * last))
    return (x0 + ccx, y0 + ccy), outline

def smooth(pts, n=2):
    p = np.array(pts)
    for _ in range(n):
        p = (np.roll(p, 1, 0) + p + np.roll(p, -1, 0)) / 3
    return [tuple(q) for q in p]

def build_leaf(name, cx, cy, scale_h=LEAF_H):
    res = trace_leaf(cx, cy)
    if not res:
        print('NO LEAF', cx, cy); return None
    (cxp, cyp), outline = res
    outline = smooth(outline, 3)
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
    pw, ph = max(xs) - min(xs), max(ys) - min(ys)
    s = scale_h / ph
    # verts: centroid fan, XZ plane (normal -Y), then V-fold along vertical
    verts = [(0.0, 0.0, 0.0)]
    for px_, py_ in outline:
        lx, lz = (px_ - cxp) * s, -(py_ - cyp) * s   # image y-down -> z-up
        ly = abs(lx) * FOLD * s * 100 / 100        # V fold: sides back in +Y
        verts.append((lx, -ly, lz))
    n = len(outline)
    faces = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    me = bpy.data.meshes.new(name + 'Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    # UV = pixel position / image size (v: image row / H)
    uvl = me.uv_layers.new(name='UVMap')
    uvl.data[0].uv = (cxp / W, cyp / H)
    for i, loop in enumerate(me.loops):
        if loop.vertex_index == 0:
            continue
        op = outline[loop.vertex_index - 1]
        uvl.data[i].uv = (op[0] / W, op[1] / H)
    ob = bpy.data.objects.new(name, me)
    col(STUDIO).objects.link(ob)
    return ob

# ---------------- material ----------------
m = bpy.data.materials.get('MapleLeaf2') or bpy.data.materials.new('MapleLeaf2')
m.use_nodes = True
nt = m.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Roughness'].default_value = 0.5
if bsdf.inputs.get('Emission Strength'):
    bsdf.inputs['Emission Strength'].default_value = 0.35
tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(IMG_COLOR)
hue = nt.nodes.new('ShaderNodeHueSaturation')
hue.inputs['Hue'].default_value = 0.34       # yellow -> red-orange
hue.inputs['Saturation'].default_value = 1.45
hue.inputs['Value'].default_value = 1.05
oi = nt.nodes.new('ShaderNodeObjectInfo')
mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs['To Min'].default_value = 0.85
mr.inputs['To Max'].default_value = 1.2
nt.links.new(tex.outputs['Color'], hue.inputs['Color'])
nt.links.new(oi.outputs['Random'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], hue.inputs['Value'])
nt.links.new(hue.outputs['Color'], bsdf.inputs['Base Color'])
if bsdf.inputs.get('Emission Color'):
    nt.links.new(hue.outputs['Color'], bsdf.inputs['Emission Color'])
# normal + roughness maps
ntex = nt.nodes.new('ShaderNodeTexImage')
ntex.image = bpy.data.images.load(IMG_NORM)
ntex.image.colorspace_settings.name = 'Non-Color'
nmap = nt.nodes.new('ShaderNodeNormalMap')
nmap.inputs['Strength'].default_value = 0.8
nt.links.new(ntex.outputs['Color'], nmap.inputs['Color'])
nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
rtex = nt.nodes.new('ShaderNodeTexImage')
rtex.image = bpy.data.images.load(IMG_ROUGH)
rtex.image.colorspace_settings.name = 'Non-Color'
nt.links.new(rtex.outputs['Color'], bsdf.inputs['Roughness'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# ---------------- build 3 leaf variants ----------------
cells = [(0, 0), (2, 0), (3, 1)]
leaf_obs = []
for i, (cx, cy) in enumerate(cells):
    ob = build_leaf(f'RealLeaf_{i}', cx, cy)
    if ob:
        if not len(ob.data.materials):
            ob.data.materials.append(m)
        leaf_obs.append(ob)
        print('leaf', i, 'verts', len(ob.data.vertices))

# ---------------- cluster: 3 leaves on a twig point ----------------
for i, ob in enumerate(leaf_obs):
    c = ob.copy()
    c.data = ob.data
    c.name = f'Clu_{i}'
    col(STUDIO).objects.link(c)
    ang = math.radians(-50 + 50 * i)
    c.rotation_euler = (math.radians(15), 0, ang)
    c.location = (0.8, 0, 0)
# twig: thin cylinder through cluster base
bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.35, location=(0.8, 0, -0.12),
                                    rotation=(0, 0, 0))
twig = bpy.context.object
twig.name = 'ClusterTwig'
move_to_col(twig, col(STUDIO))
bark = bpy.data.materials.get('TwigMat') or bpy.data.materials.new('TwigMat')
bark.use_nodes = True
b = next(n for n in bark.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
b.inputs['Base Color'].default_value = (0.05, 0.02, 0.015, 1)
twig.data.materials.append(bark)

# ---------------- isolate: hide every collection except LEAF_STUDIO ----------------
for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    lc.exclude = (lc.name != STUDIO)

# backdrop plane behind leaf
bpy.ops.mesh.primitive_plane_add(size=8, location=(0.4, 0.8, 0.1))
bp = bpy.context.object; bp.name = 'StudioBackdrop'
move_to_col(bp, col(STUDIO))
bpm = bpy.data.materials.get('StudioBg') or bpy.data.materials.new('StudioBg')
bpm.use_nodes = True
bb = next(n for n in bpm.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
bb.inputs['Base Color'].default_value = (0.03, 0.035, 0.05, 1)
bb.inputs['Roughness'].default_value = 0.95
bp.data.materials.append(bpm)

# lights: back sun (translucency) + front area fill
sun = bpy.data.objects.new('StudioSun', bpy.data.lights.new('StudioSun', 'SUN'))
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(30), 0, math.radians(160))
col(STUDIO).objects.link(sun)
area = bpy.data.objects.new('StudioArea', bpy.data.lights.new('StudioArea', 'AREA'))
area.data.energy = 300
area.data.shape = 'DISK'; area.data.size = 1.2
area.location = (0, -1.5, 0.6)
area.rotation_euler = (math.radians(90), 0, 0)
col(STUDIO).objects.link(area)

# world: dim warm gray
w = bpy.context.scene.world
for n in w.node_tree.nodes:
    if n.bl_idname == 'ShaderNodeBackground':
        n.inputs['Color'].default_value = (0.02, 0.025, 0.04, 1)
        n.inputs['Strength'].default_value = 0.4

# camera
cam = bpy.data.objects['Camera']
cam.data.lens = 70
cam.data.dof.use_dof = False

# ---------------- renders ----------------
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100
try:
    s.cycles.samples = 64
except Exception:
    pass

# hide cluster for single render
clu = [o for o in col(STUDIO).objects if o.name.startswith('Clu_') or o.name == 'ClusterTwig']
single = leaf_obs[0]
for o in clu: o.hide_render = True
for o in leaf_obs[1:]: o.hide_render = True
cam.location = (0, -1.0, 0.0)
cam.rotation_euler = (math.radians(90), 0, 0)
s.render.filepath = os.path.join(RENDER_DIR, 'p10_leaf_single.png')
bpy.ops.render.render(write_still=True)
print('RENDERED single')

# cluster render
for o in clu: o.hide_render = False
single.hide_render = True
cam.location = (0.8, -1.3, 0.1)
s.render.filepath = os.path.join(RENDER_DIR, 'p10_leaf_cluster.png')
bpy.ops.render.render(write_still=True)
print('RENDERED cluster')

save()
print('P10 DONE')
