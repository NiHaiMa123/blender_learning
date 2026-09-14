"""Phase 14: inspection lighting (key + fill + rim) and final near/mid/far
tree-only renders."""
import bpy, math, sys
from mathutils import Vector, Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR
import os

# ---------- inspection lighting ----------
lcol = col('TREE_VIEW_LIGHTS')

def area(name, loc, energy, size, color):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy
    ld.shape = 'DISK'
    ld.size = size
    ld.color = color
    o = bpy.data.objects.new(name, ld)
    lcol.objects.link(o)
    o.location = loc
    # aim at trunk center (-4.5, 0, 4)
    d = Vector((-4.5, 0, 4.0)) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

for o in list(lcol.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# key: warm, camera-right-high
area('key', (2.0, -6.0, 9.0), 1400, 5.0, (1.0, 0.88, 0.78))
# fill: cool, camera-left-low
area('fill', (-9.0, -5.0, 5.0), 900, 4.0, (0.72, 0.80, 1.0))
# rim: from behind-right to edge the silhouette (tight, above crown so the
# spot on the backdrop stays out of frame)
area('rim', (-2.0, 7.0, 11.0), 400, 2.0, (1.0, 0.75, 0.60))

# world: dark neutral gray backdrop, slight ambient
w = bpy.context.scene.world
if w and w.use_nodes:
    bg = next((n for n in w.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground'), None)
    if bg:
        bg.inputs[0].default_value = (0.035, 0.04, 0.05, 1)
        bg.inputs[1].default_value = 0.6

# ---------- cameras & renders ----------
cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = False
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1400
s.render.resolution_percentage = 100

def look_at(c, target):
    d = Vector(target) - c.location
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

# NEAR: bark/ridge/hollow detail around the S-bend — show hollow + upper trunk
cam.data.lens = 60
cam.location = (-2.2, -6.0, 3.8)
look_at(cam, (-5.0, 0.1, 3.6))
s.render.filepath = os.path.join(RENDER_DIR, 'p14_near.png')
bpy.ops.render.render(write_still=True)
print('RENDERED near')

# MID: whole tree silhouette — pulled back so limb tips stay in frame
cam.data.lens = 46
cam.location = (-1.6, -18.5, 4.8)
look_at(cam, (-3.2, 0.1, 4.4))
s.render.filepath = os.path.join(RENDER_DIR, 'p14_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED mid')

# FAR: tree small in wide frame
cam.data.lens = 32
cam.location = (-0.8, -30.0, 5.2)
look_at(cam, (-3.4, 0.1, 4.0))
s.render.filepath = os.path.join(RENDER_DIR, 'p14_far.png')
bpy.ops.render.render(write_still=True)
print('RENDERED far')

save()
print('P14 DONE')
