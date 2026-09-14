"""Phase 10g: backlit-dominant lighting so maple reads deep red;
shorten twig so it ends inside the stem bundle."""
import bpy, math, os, sys
from mathutils import Euler, Vector
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import save, RENDER_DIR

# lighting: kill the flat frontal wash, keep strong rim/backlight
area = bpy.data.objects.get('StudioArea')
if area:
    area.data.energy = 45          # gentle frontal fill only
    area.data.size = 1.5           # softer
fill = bpy.data.objects.get('StudioFill')
if fill:
    fill.data.energy = 25
sun = bpy.data.objects.get('StudioSun')
if sun:
    sun.data.energy = 3.0          # backlight drives translucency feel

# a rim area from behind-left for extra edge separation
rim = bpy.data.objects.get('StudioRim')
if not rim:
    rim = bpy.data.objects.new('StudioRim', bpy.data.lights.new('StudioRim', 'AREA'))
    col = bpy.data.collections.get('LEAF_STUDIO')
    col.objects.link(rim)
rim.data.energy = 250
rim.data.size = 0.6
rim.location = (0.3, 0.9, 0.5)
rim.rotation_euler = Euler((math.radians(130), 0, math.radians(180)), 'XYZ')

# twig: shorten to ~10cm ending at stem convergence
twig = bpy.data.objects.get('ClusterTwig')
if twig:
    twig.scale = (0.7, 0.7, 0.28)
    twig.location = Vector((0.9, 0.0, 0.02))
    twig.hide_render = True

cam = bpy.data.objects['Camera']
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_x = s.render.resolution_y = 1200
s.render.resolution_percentage = 100

# single closeup
for i in (1, 2):
    bpy.data.objects[f'LeafCard_{i}'].hide_render = True
leaf0 = bpy.data.objects['LeafCard_0']
leaf0.hide_render = False
leaf0.location = (0, 0, 0)
leaf0.rotation_euler = (0, 0, 0)
cam.data.lens = 55
cam.location = (0, -0.85, 0.02)
cam.rotation_euler = Euler((math.radians(90), 0, 0), 'XYZ')
s.render.filepath = os.path.join(RENDER_DIR, 'p10g_single.png')
bpy.ops.render.render(write_still=True)

# cluster
leaf0.hide_render = True
for i in range(7):
    bpy.data.objects[f'Clu_{i}'].hide_render = False
if twig:
    twig.hide_render = False
cam.data.lens = 50
cam.location = (0.9, -1.15, 0.12)
s.render.filepath = os.path.join(RENDER_DIR, 'p10g_cluster.png')
bpy.ops.render.render(write_still=True)

save()
print('P10G DONE')
