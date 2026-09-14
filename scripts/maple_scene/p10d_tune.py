"""Phase 10d: fix leaf color (luminance->red ramp instead of hue shift),
clean leaf bboxes (auto non-edge components), bigger backdrop, proper
cluster arrangement (stems converge at twig tip)."""
import bpy, math, os, sys
import numpy as np
from collections import deque
from mathutils import Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR

TEX = r'C:/Users/Administrator/AppData/Local/Temp/leafref/LeafSet021'
IMG_OPAC = os.path.join(TEX, 'LeafSet021_1K-JPG_Opacity.jpg')
STUDIO = 'LEAF_STUDIO'
W, H = 1024, 512

# ---------------- recompute leaf components, pick clean ones ----------------
op_img = bpy.data.images.load(IMG_OPAC)
op_img.update()
px = np.array(op_img.pixels[:], dtype=np.float32).reshape(H, W, 4)
mask = px[:, :, 0] > 0.5
lab = np.zeros(mask.shape, dtype=np.int32)
nl = 0
for y in range(H):
    for x in range(W):
        if mask[y, x] and lab[y, x] == 0:
            nl += 1
            q = deque([(x, y)]); lab[y, x] = nl
            while q:
                cx_, cy_ = q.popleft()
                for nx_, ny_ in ((cx_+1,cy_),(cx_-1,cy_),(cx_,cy_+1),(cx_,cy_-1)):
                    if 0 <= nx_ < W and 0 <= ny_ < H and mask[ny_, nx_] and lab[ny_, nx_] == 0:
                        lab[ny_, nx_] = nl
                        q.append((nx_, ny_))
boxes = []
for i in range(1, nl + 1):
    ys, xs = np.nonzero(lab == i)
    a = len(xs)
    if a < 3000:
        continue
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    edge = x0 < 6 or y0 < 6 or x1 > W - 7 or y1 > H - 7
    boxes.append({'id': i, 'area': a, 'box': (x0, y0, x1, y1), 'edge': edge})
boxes.sort(key=lambda b: -b['area'])
clean = [b for b in boxes if not b['edge']]
print('clean leaves:', [(b['area'], b['box']) for b in clean[:6]])

# ---------------- rebuild card UVs to clean bboxes ----------------
FOLD = math.radians(20)
def recard(name, box):
    x0, y0, x1, y1 = box
    pad = 2
    u0, v0 = (x0 - pad) / W, (y0 - pad) / H
    u1, v1 = (x1 + pad) / W, (y1 + pad) / H
    um = (u0 + u1) / 2
    ar = (x1 - x0) / (y1 - y0)
    w, h = 0.25 * ar, 0.25
    fy = (w / 2) * math.tan(FOLD)
    verts = [(-w/2, fy,  h/2), (-w/2, fy, -h/2),
             (0,    0,   h/2), (0,    0,  -h/2),
             (w/2,  fy,  h/2), (w/2,  fy, -h/2)]
    me = bpy.data.objects[name].data
    me.clear_geometry()
    me.from_pydata(verts, [], [(0,1,3,2), (2,3,5,4)])
    me.update()
    uvl = me.uv_layers.active or me.uv_layers.new(name='UVMap')
    uv_map = {0:(u0,v1),1:(u0,v0),2:(um,v1),3:(um,v0),4:(u1,v1),5:(u1,v0)}
    for i, loop in enumerate(me.loops):
        uvl.data[i].uv = uv_map[loop.vertex_index]
    return h / 2

half_heights = []
for i in range(3):
    box = clean[i]['box'] if i < len(clean) else boxes[i]['box']
    half_heights.append(recard(f'LeafCard_{i}', box))

# ---------------- material: luminance -> red ramp ----------------
m = bpy.data.materials['MapleLeaf2']
nt = m.node_tree
# remove hue node links, insert ramp path
hue = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeHueSaturation')
mr = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange')
oi = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeObjectInfo')
tex = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexImage')
bsdf = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
# drop hue node links
for l in list(nt.links):
    if l.to_node == hue or l.from_node == hue:
        nt.links.remove(l)
nt.nodes.remove(hue)
# luminance: tex color -> RGB to BW -> ramp(red gradient) ; random -> ramp fac jitter
bw = nt.nodes.new('ShaderNodeRGBToBW')
ramp = nt.nodes.new('ShaderNodeValToRGB')
cr = ramp.color_ramp
cr.elements.remove(cr.elements[1])
e0 = cr.elements[0]; e0.position = 0.0; e0.color = (0.06, 0.004, 0.002, 1)   # deep red
e1 = cr.elements.new(0.45); e1.color = (0.45, 0.02, 0.004, 1)               # red
e2 = cr.elements.new(0.75); e2.color = (0.85, 0.12, 0.01, 1)                # red-orange
e3 = cr.elements.new(1.0); e3.color = (1.0, 0.35, 0.05, 1)                  # amber tips
nt.links.new(tex.outputs['Color'], bw.inputs['Color'])
nt.links.new(bw.outputs['Val'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
if bsdf.inputs.get('Emission Color'):
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 0.3

# ---------------- backdrop bigger ----------------
bp = bpy.data.objects.get('StudioBackdrop')
if bp:
    bp.location = (0.4, 3.0, 0.1)
    bp.scale = (5, 5, 5)

# ---------------- cluster: stems converge at twig tip ----------------
TIP = (0.9, 0.0, 0.12)
for i in range(5):
    src_i = i % 3
    c = bpy.data.objects.get(f'Clu_{i}')
    if not c:
        continue
    a = math.radians(-65 + 32 * i)
    tilt = math.radians(-25 + 12 * i)      # leaves fan upward-outward
    c.rotation_euler = Euler((tilt, 0, a), 'XYZ')
    R = c.rotation_euler.to_matrix()
    hh = half_heights[src_i]
    # leaf local bottom-center (stem tip): (0, 0, -hh)
    import mathutils
    off = R @ mathutils.Vector((0, 0, -hh))
    c.location = mathutils.Vector(TIP) - off
    c.hide_render = True

# ---------------- renders ----------------
cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100

cam.data.lens = 45
cam.location = (0, -1.4, 0)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p10d_lineup.png')
bpy.ops.render.render(write_still=True)

for o in bpy.data.objects:
    if o.name.startswith('LeafCard_'):
        o.hide_render = o.name != 'LeafCard_0'
leaf0 = bpy.data.objects['LeafCard_0']
leaf0.location = (0, 0, 0)
leaf0.rotation_euler = (0, 0, 0)
cam.data.lens = 70
cam.location = (0, -0.8, 0.02)
s.render.filepath = os.path.join(RENDER_DIR, 'p10d_single.png')
bpy.ops.render.render(write_still=True)

leaf0.hide_render = True
for i in range(5):
    bpy.data.objects[f'Clu_{i}'].hide_render = False
twig = bpy.data.objects.get('ClusterTwig')
if twig:
    twig.location = (0.9, 0, -0.05)
    twig.hide_render = False
cam.data.lens = 50
cam.location = (0.9, -1.2, 0.1)
s.render.filepath = os.path.join(RENDER_DIR, 'p10d_cluster.png')
bpy.ops.render.render(write_still=True)

save()
print('P10D DONE')
