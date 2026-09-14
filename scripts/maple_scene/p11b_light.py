"""Phase 11b: trunk studio lighting fix + deeper ridges + stronger moss."""
import bpy, math, os, sys
from mathutils import Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, save, RENDER_DIR

# hide leaf studio props for trunk shots
for o in bpy.data.collections['LEAF_STUDIO'].objects:
    if o.name.startswith(('LeafCard', 'Clu_', 'RealLeaf')) or o.name in ('ClusterTwig', 'StarDeep', 'StarSoft'):
        o.hide_render = True

# dedicated trunk key light (front-left of trunk at x=-4.7)
key = bpy.data.objects.get('TrunkKey')
if not key:
    key = bpy.data.objects.new('TrunkKey', bpy.data.lights.new('TrunkKey', 'AREA'))
    bpy.data.collections['LEAF_STUDIO'].objects.link(key)
key.data.energy = 900
key.data.size = 2.0
key.data.color = (1.0, 0.85, 0.7)
key.location = (-2.5, -3.5, 3.5)
key.rotation_euler = Euler((math.radians(55), 0, math.radians(-30)), 'XYZ')

# warm rim from behind-right to separate from bg
rim2 = bpy.data.objects.get('TrunkRim')
if not rim2:
    rim2 = bpy.data.objects.new('TrunkRim', bpy.data.lights.new('TrunkRim', 'AREA'))
    bpy.data.collections['LEAF_STUDIO'].objects.link(rim2)
rim2.data.energy = 700
rim2.data.size = 1.5
rim2.data.color = (1.0, 0.6, 0.35)
rim2.location = (-6.5, 1.5, 4.0)
rim2.rotation_euler = Euler((math.radians(120), 0, math.radians(160)), 'XYZ')

sun = bpy.data.objects.get('StudioSun')
if sun:
    sun.data.energy = 1.5

# deeper ridges
sd = bpy.data.objects.get('StarDeep')
if sd:
    sp = sd.data.splines[0]
    for i, p in enumerate(sp.points):
        a = 2 * math.pi * i / len(sp.points)
        ph = (i % 4) / 4
        inner = 0.55
        r = inner + (1 - inner) * (0.5 - 0.5 * math.cos(2 * math.pi * ph))
        p.co = (math.cos(a) * r, math.sin(a) * r, 0, 1)
    sd.data.update_tag()

# moss: widen mask range, boost green
m = bpy.data.materials['Bark']
nt = m.node_tree
mrg = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange')
mrg.inputs['From Min'].default_value = 0.05
mrg.inputs['From Max'].default_value = 0.55
mix = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMix')
mix.inputs['B'].default_value = (0.16, 0.14, 0.02, 1)
mn = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexNoise' and n.inputs['Scale'].default_value < 5)
mn.inputs['Scale'].default_value = 1.6

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1400
s.render.resolution_percentage = 100

cam.data.lens = 50
cam.location = (-4.7, -5.2, 2.6)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p11b_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED mid')

cam.location = (-4.7, -3.0, 0.9)
cam.data.lens = 40
s.render.filepath = os.path.join(RENDER_DIR, 'p11b_base.png')
bpy.ops.render.render(write_still=True)
print('RENDERED base')

save()
print('P11B DONE')
