"""Phase 13: branch collars at junctions + trunk hollow at the S-bend
(reference has a dark cavity on the upper-left curl). Then near/far renders."""
import bpy, math, sys
from mathutils import Vector, Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR
import os

bark = bpy.data.materials['Bark']
tree_col = col('TREE')
trunk = bpy.data.objects['MapleTree']

# ---------- branch collars: ellipsoid bulge at each limb base ----------
collars = [
    (-3.88, 0.10, 5.55, 0.26),  # limbA base — small, embedded
    (-3.78, 0.08, 5.50, 0.28),  # limbB base
    (-3.80, -0.02, 5.45, 0.18), # limbC
    (-4.02, -0.05, 5.20, 0.15), # limbD
    (-3.90, 0.14, 5.38, 0.16),  # limbE
]
for i, (x, y, z, r) in enumerate(collars):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(x, y, z))
    s = bpy.context.object
    s.name = f'collar{i}'
    s.scale = (r, r * 0.55, r * 1.1)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for uc in list(s.users_collection):
        uc.objects.unlink(s)
    tree_col.objects.link(s)
    s.data.materials.append(bark)
    for p in s.data.polygons:
        p.use_smooth = True

# join collars into trunk
bpy.ops.object.select_all(action='DESELECT')
for o in tree_col.objects:
    if o.type == 'MESH':
        o.select_set(True)
bpy.context.view_layer.objects.active = trunk
bpy.ops.object.join()
trunk = bpy.context.object
trunk.name = 'MapleTree'

# ---------- trunk hollow: dark recessed cavity on the S inner bend ----------
# reference: dark hole on the left-curl inner face around z~3.2, facing -Y/left
hollow_mat = bpy.data.materials.get('HollowDark') or bpy.data.materials.new('HollowDark')
hollow_mat.use_nodes = True
hb = next(n for n in hollow_mat.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
hb.inputs['Base Color'].default_value = (0.0004, 0.0003, 0.0002, 1)
hb.inputs['Roughness'].default_value = 1.0
hb.inputs['Specular IOR Level'].default_value = 0.0

bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(-5.62, -0.62, 3.30))
hol = bpy.context.object
hol.name = 'TrunkHollow'
hol.scale = (0.26, 0.14, 0.42)          # shallow dish pressed into trunk
hol.rotation_euler = Euler((math.radians(-15), math.radians(25), 0), 'XYZ')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for uc in list(hol.users_collection):
    uc.objects.unlink(hol)
tree_col.objects.link(hol)
hol.data.materials.append(hollow_mat)
for p in hol.data.polygons:
    p.use_smooth = True
# rim ring: torus around the hollow opening for the raised callus edge
bpy.ops.mesh.primitive_torus_add(major_radius=0.24, minor_radius=0.06,
                                 major_segments=24, minor_segments=8,
                                 location=(-5.64, -0.64, 3.30),
                                 rotation=(math.radians(90), math.radians(8), 0))
rim = bpy.context.object
rim.name = 'HollowRim'
rim.scale = (0.95, 0.95, 1.5)
for uc in list(rim.users_collection):
    uc.objects.unlink(rim)
tree_col.objects.link(rim)
rim.data.materials.append(bark)
for p in rim.data.polygons:
    p.use_smooth = True

# ---------- renders: near / mid / far ----------
cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = False
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 100

# NEAR: trunk detail + hollow
s.render.resolution_x = s.render.resolution_y = 1400
cam.data.lens = 55
cam.location = (-4.2, -4.5, 3.2)
cam.rotation_euler = Euler((math.radians(90), 0, math.radians(-8)), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p13_near.png')
bpy.ops.render.render(write_still=True)
print('RENDERED near')

# MID: whole tree silhouette
cam.data.lens = 42
cam.location = (-1.2, -14.0, 4.6)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p13_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED mid')

# FAR: wide, tree small in frame
cam.data.lens = 30
cam.location = (-0.8, -26.0, 5.0)
s.render.filepath = os.path.join(RENDER_DIR, 'p13_far.png')
bpy.ops.render.render(write_still=True)
print('RENDERED far')

save()
print('P13 DONE')
