"""Phase 28: render MY tree as black silhouette on white, same framing as
extracted reference mask — for direct outline comparison."""
import bpy, math, sys
from mathutils import Vector
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR
import os

# isolate tree only (no studio backdrop, no lights needed — emission is flat)
for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    lc.exclude = lc.name != 'TREE'

# pure black emission material on all tree faces
sil = bpy.data.materials.get('Silhouette')
if not sil:
    sil = bpy.data.materials.new('Silhouette')
    sil.use_nodes = True
    nt = sil.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (0, 0, 0, 1)
    em.inputs['Strength'].default_value = 1.0
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])

trunk = bpy.data.objects['MapleTree']
saved_mats = [m for m in trunk.data.materials]
trunk.data.materials.clear()
trunk.data.materials.append(sil)

# white world
w = bpy.context.scene.world
if w and w.use_nodes:
    bg = next((n for n in w.node_tree.nodes if n.bl_idname == 'ShaderNodeBackground'), None)
    if bg:
        bg.inputs[0].default_value = (1, 1, 1, 1)
        bg.inputs[1].default_value = 1.0

# same-ish framing as reference: wide ratio, tree left-of-center, low camera
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = 1536
s.render.resolution_y = 687
s.render.resolution_percentage = 100
cam = bpy.data.objects['Camera']
cam.data.dof.use_dof = False
cam.data.lens = 42
cam.location = (-1.8, -21.0, 4.2)
d = Vector((-3.6, 0.2, 4.6)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
s.render.filepath = os.path.join(RENDER_DIR, 'my_tree_silhouette.png')
bpy.ops.render.render(write_still=True)
print('RENDERED silhouette')

# restore materials + world
trunk.data.materials.clear()
for m in saved_mats:
    trunk.data.materials.append(m)
if w and w.use_nodes and bg:
    bg.inputs[0].default_value = (0.035, 0.04, 0.05, 1)
    bg.inputs[1].default_value = 0.6
save()
print('P28 DONE')
