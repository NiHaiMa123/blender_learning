"""Phase 11c: real bark texture via Generated coords + restrained moss +
deeper ridges. Kills the smooth-clay look."""
import bpy, math, os, sys
from mathutils import Euler
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import save, RENDER_DIR

BARK_IMG = r'D:/project/blender_learning/scripts/asset_tex/archmodels52_030_bark_diffuse_jpg.jpg'

# ---------- rebuild Bark material: photo tex (generated/box) + furrow bump ----------
m = bpy.data.materials['Bark']
nt = m.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Roughness'].default_value = 0.85

tc = nt.nodes.new('ShaderNodeTexCoord')
mp = nt.nodes.new('ShaderNodeMapping')
# stretch texture along trunk length so grain runs vertically
mp.inputs['Scale'].default_value = (2.0, 2.0, 0.6)
tex = nt.nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(BARK_IMG)
tex.extension = 'REPEAT'
nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])

# darken photo bark toward maple-dark
bc = nt.nodes.new('ShaderNodeBrightContrast')
bc.inputs['Bright'].default_value = -0.28
bc.inputs['Contrast'].default_value = 0.12
nt.links.new(tex.outputs['Color'], bc.inputs['Color'])

# moss: only patches — noise-gated upfacing
geo = nt.nodes.new('ShaderNodeNewGeometry')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
mrg = nt.nodes.new('ShaderNodeMapRange')
mrg.inputs['From Min'].default_value = 0.3
mrg.inputs['From Max'].default_value = 0.8
mrg.clamp = True
mn = nt.nodes.new('ShaderNodeTexNoise')
mn.inputs['Scale'].default_value = 3.5
mn.inputs['Detail'].default_value = 4.0
mn.inputs['Roughness'].default_value = 0.7
mr2 = nt.nodes.new('ShaderNodeMapRange')
mr2.inputs['From Min'].default_value = 0.45
mr2.inputs['From Max'].default_value = 0.72
mr2.clamp = True
mult = nt.nodes.new('ShaderNodeMath'); mult.operation = 'MULTIPLY'
mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
mix.inputs['B'].default_value = (0.11, 0.10, 0.015, 1)
nt.links.new(geo.outputs['Normal'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Z'], mrg.inputs['Value'])
nt.links.new(geo.outputs['Position'], mn.inputs['Vector'])
nt.links.new(mn.outputs['Fac'], mr2.inputs['Value'])
nt.links.new(mrg.outputs['Result'], mult.inputs[0])
nt.links.new(mr2.outputs['Result'], mult.inputs[1])
nt.links.new(mult.outputs[0], mix.inputs['Factor'])
nt.links.new(bc.outputs['Color'], mix.inputs['A'])
nt.links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])

# bump: photo texture bump + stretched-wave furrows
bump1 = nt.nodes.new('ShaderNodeBump')
bump1.inputs['Strength'].default_value = 0.45
bump1.inputs['Distance'].default_value = 0.04
nt.links.new(tex.outputs['Color'], bump1.inputs['Height'])
wave = nt.nodes.new('ShaderNodeTexWave')
wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'
wave.inputs['Scale'].default_value = 5.0
wave.inputs['Distortion'].default_value = 8.0
wave.inputs['Detail'].default_value = 6.0
wave.inputs['Detail Scale'].default_value = 2.5
bump2 = nt.nodes.new('ShaderNodeBump')
bump2.inputs['Strength'].default_value = 0.5
bump2.inputs['Distance'].default_value = 0.06
nt.links.new(mp.outputs['Vector'], wave.inputs['Vector'])
nt.links.new(wave.outputs['Color'], bump2.inputs['Height'])
nt.links.new(bump1.outputs['Normal'], bump2.inputs['Normal'])
nt.links.new(bump2.outputs['Normal'], bsdf.inputs['Normal'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# ---------- deeper ridges ----------
sd = bpy.data.objects.get('StarDeep')
sp = sd.data.splines[0]
n = len(sp.points)
for i, p in enumerate(sp.points):
    a = 2 * math.pi * i / n
    ph = (i % 4) / 4
    inner = 0.50
    r = inner + (1 - inner) * (0.5 - 0.5 * math.cos(2 * math.pi * ph))
    p.co = (math.cos(a) * r, math.sin(a) * r, 0, 1)
sd.data.update_tag()

# sink trunk base slightly to hide cap artifact
tr = bpy.data.objects.get('MapleTree')
if tr:
    tr.location.z = -0.15

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1400
s.render.resolution_percentage = 100

cam.data.lens = 50
cam.location = (-4.7, -5.2, 2.6)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p11c_mid.png')
bpy.ops.render.render(write_still=True)
print('RENDERED mid')

cam.location = (-4.7, -3.0, 0.9)
cam.data.lens = 40
s.render.filepath = os.path.join(RENDER_DIR, 'p11c_base.png')
bpy.ops.render.render(write_still=True)
print('RENDERED base')

save()
print('P11C DONE')
