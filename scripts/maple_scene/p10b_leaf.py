"""Phase 10b: fix leaf tracing — connected components on opacity map,
radial outline per component, FLAT fan mesh (fold later via modifier),
toned-down red grading. Renders: lineup + single closeup + cluster.
"""
import bpy, math, os, sys
import numpy as np
from collections import deque
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, move_to_col, save, RENDER_DIR

TEX = r'C:/Users/Administrator/AppData/Local/Temp/leafref/LeafSet021'
IMG_COLOR = os.path.join(TEX, 'LeafSet021_1K-JPG_Color.jpg')
IMG_OPAC = os.path.join(TEX, 'LeafSet021_1K-JPG_Opacity.jpg')
IMG_NORM = os.path.join(TEX, 'LeafSet021_1K-JPG_NormalGL.jpg')
IMG_ROUGH = os.path.join(TEX, 'LeafSet021_1K-JPG_Roughness.jpg')

STUDIO = 'LEAF_STUDIO'
NRAYS = 160
LEAF_H = 0.25

# ---------------- find leaf components ----------------
op_img = bpy.data.images.load(IMG_OPAC)
op_img.update()
W, H = op_img.size
px = np.array(op_img.pixels[:], dtype=np.float32).reshape(H, W, 4)
mask = px[:, :, 0] > 0.5
lab = np.zeros(mask.shape, dtype=np.int32)
nl = 0
for y in range(H):
    row = mask[y]
    for x in range(W):
        if row[x] and lab[y, x] == 0:
            nl += 1
            q = deque([(x, y)]); lab[y, x] = nl
            while q:
                cx_, cy_ = q.popleft()
                for nx_, ny_ in ((cx_+1,cy_),(cx_-1,cy_),(cx_,cy_+1),(cx_,cy_-1)):
                    if 0 <= nx_ < W and 0 <= ny_ < H and mask[ny_, nx_] and lab[ny_, nx_] == 0:
                        lab[ny_, nx_] = nl
                        q.append((nx_, ny_))
areas = [(int((lab == i).sum()), i) for i in range(1, nl + 1)]
areas.sort(reverse=True)
print('components', nl, 'top areas', [a for a, _ in areas[:10]])

def comp_info(cid):
    ys, xs = np.nonzero(lab == cid)
    return xs, ys, xs.min(), ys.min(), xs.max(), ys.max(), xs.mean(), ys.mean()

def trace(cid, mx, my, pad=4):
    _, _, x0, y0, x1, y1, ccx, ccy = comp_info(cid)
    m = (lab[y0:y1+1, x0:x1+1] == cid)
    ch, cw = m.shape
    lx, ly = ccx - x0, ccy - y0
    out = []
    for i in range(NRAYS):
        a = 2 * math.pi * i / NRAYS
        dx, dy = math.cos(a), math.sin(a)
        r, last = 0.0, 0.0
        while r < max(cw, ch) * 1.5:
            ix, iy = int(lx + dx * r), int(ly + dy * r)
            if ix < 0 or iy < 0 or ix >= cw or iy >= ch or not m[iy, ix]:
                break
            last = r
            r += 0.6
        out.append((x0 + lx + dx * last, y0 + ly + dy * last))
    return (ccx, ccy), out

def smooth(pts, n=2):
    p = np.array(pts)
    for _ in range(n):
        p = (np.roll(p, 1, 0) + p + np.roll(p, -1, 0)) / 3
    return [tuple(q) for q in p]

def build_leaf(name, cid, scale_h=LEAF_H):
    (ccx, ccy), outline = trace(cid, 0, 0)
    outline = smooth(outline, 3)
    xs = [p[0] for p in outline]; ys = [p[1] for p in outline]
    pw, ph = max(xs) - min(xs), max(ys) - min(ys)
    s = scale_h / ph
    verts = [(0.0, 0.0, 0.0)]
    for px_, py_ in outline:
        lx, lz = (px_ - ccx) * s, -(py_ - ccy) * s
        verts.append((lx, 0.0, lz))          # flat for now
    n = len(outline)
    faces = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    me = bpy.data.meshes.new(name + 'Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    uvl = me.uv_layers.new(name='UVMap')
    uvl.data[0].uv = (ccx / W, ccy / H)
    for i, loop in enumerate(me.loops):
        if loop.vertex_index:
            op = outline[loop.vertex_index - 1]
            uvl.data[i].uv = (op[0] / W, op[1] / H)
    old = bpy.data.objects.get(name)
    if old:
        old.data = me
        return old
    ob = bpy.data.objects.new(name, me)
    col(STUDIO).objects.link(ob)
    return ob

# pick 3 largest components
cids = [cid for _, cid in areas[:3]]
mats = bpy.data.materials['MapleLeaf2']
nt = mats.node_tree
hue = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeHueSaturation')
hue.inputs['Hue'].default_value = 0.30
hue.inputs['Saturation'].default_value = 1.15
hue.inputs['Value'].default_value = 1.15
bsdf = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
if bsdf.inputs.get('Emission Strength'):
    bsdf.inputs['Emission Strength'].default_value = 0.18
mr = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange')
mr.inputs['To Min'].default_value = 0.9
mr.inputs['To Max'].default_value = 1.15

leaf_obs = []
for i, cid in enumerate(cids):
    ob = build_leaf(f'RealLeaf_{i}', cid)
    if len(ob.data.materials) == 0:
        ob.data.materials.append(mats)
    ob.location = (i * 0.4 - 0.4, 0, 0)
    leaf_obs.append(ob)
    xs, ys, x0, y0, x1, y1, mx, my = comp_info(cid)
    print('leaf', i, 'bbox', (x0, y0, x1, y1), 'px', x1-x0, 'x', y1-y0)

# cluster copies
for i, ob in enumerate(leaf_obs):
    c = bpy.data.objects.get(f'Clu_{i}') or ob.copy()
    if not c.users_collection:
        col(STUDIO).objects.link(c)
    c.data = ob.data
    c.rotation_euler = (math.radians(15), 0, math.radians(-50 + 50 * i))
    c.location = (0.8, 0, 0)
    c.hide_render = True

# renders
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100
cam = bpy.data.objects['Camera']
cam.data.lens = 55
cam.data.dof.use_dof = False

# lineup of 3 leaves
cam.location = (0, -1.6, 0)
cam.rotation_euler = (math.radians(90), 0, 0)
s.render.filepath = os.path.join(RENDER_DIR, 'p10b_lineup.png')
bpy.ops.render.render(write_still=True)
print('RENDERED lineup')

# single closeup
for o in leaf_obs[1:]:
    o.hide_render = True
leaf_obs[0].location = (0, 0, 0)
cam.location = (0, -0.9, 0)
cam.data.lens = 70
s.render.filepath = os.path.join(RENDER_DIR, 'p10b_single.png')
bpy.ops.render.render(write_still=True)
print('RENDERED single')

save()
print('P10B DONE')
