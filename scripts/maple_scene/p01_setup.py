exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

scene = bpy.context.scene

# ---- render settings: Cycles final, wide cinematic frame ----
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 2560
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 50
scene.cycles.samples = 128
scene.cycles.use_denoising = True
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception as e:
    print('look fail:', e)

# ---- world: soft blue sky ----
w = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
scene.world = w
w.use_nodes = True
bg = w.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.32, 0.48, 0.75, 1)
bg.inputs['Strength'].default_value = 0.6

# ---- camera: low, wide, slight tilt up ----
cam = bpy.data.objects.get('Camera')
if not cam:
    cam = bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))
    scene.collection.objects.link(cam)
cam.location = (0.5, -13.0, 1.1)
cam.rotation_euler = (math.radians(99), 0, 0)
cam.data.lens = 26
scene.camera = cam

# ---- default light -> sun from right-rear (backlight) ----
light = bpy.data.objects.get('Light')
if light:
    light.data.type = 'SUN'
    light.data.energy = 4.0
    light.rotation_euler = (math.radians(35), math.radians(-25), math.radians(120))
    light.name = 'Sun'

# ---- placeholder geometry for composition check ----
ph = col('PLACEHOLDER')

bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=8, location=(-4.5, 0, 3.4),
                                    rotation=(0, math.radians(14), 0))
o = bpy.context.object; o.name = 'PH_trunk'; move_to_col(o, ph)

bpy.ops.mesh.primitive_ico_sphere_add(radius=3.8, subdivisions=2,
                                      location=(-2.8, 0, 7.5), scale=(1.5, 1.0, 0.6))
o = bpy.context.object; o.name = 'PH_canopy'; move_to_col(o, ph)

bpy.ops.mesh.primitive_plane_add(size=80)
o = bpy.context.object; o.name = 'PH_ground'; move_to_col(o, ph)

save()
render_preview('p01_composition.png')
