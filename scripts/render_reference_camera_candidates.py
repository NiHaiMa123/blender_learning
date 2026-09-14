import bpy, os
from mathutils import Vector

scene = bpy.data.scenes['Codex_Cycles_Render']
cam = scene.camera
bpy.context.window.scene = scene

old_cam = (
    cam.location.copy(), cam.rotation_euler.copy(), cam.data.lens,
    cam.data.sensor_fit, cam.data.shift_x, cam.data.shift_y,
)
old_render = (
    scene.render.filepath, scene.render.resolution_x, scene.render.resolution_y,
    scene.render.resolution_percentage, scene.cycles.samples,
)

candidates = [
    # Near-frontal product/statue framing, with the whole figure retained.
    ('front_78mm', Vector((0.02, -6.00, 0.95)), Vector((-0.02, 0.00, 0.86)), 78),
    # Slight horizontal offset, closest to the reference's subtle 3/4 view.
    ('reference_78mm', Vector((0.30, -6.00, 0.93)), Vector((-0.03, 0.00, 0.86)), 78),
    # A touch lower, to test whether the reference reads as a mild low angle.
    ('low_78mm', Vector((0.30, -6.00, 0.74)), Vector((-0.03, 0.00, 0.86)), 78),
]

paths = []
try:
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.shift_x = 0.0
    cam.data.shift_y = 0.0
    scene.render.resolution_x = 360
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    for name, location, target, lens in candidates:
        cam.location = location
        cam.rotation_euler = (target - location).to_track_quat('-Z', 'Y').to_euler()
        cam.data.lens = lens
        path = fr'D:\project\blender_learning\renders\camera_{name}.png'
        scene.render.filepath = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
finally:
    cam.location, cam.rotation_euler, cam.data.lens, cam.data.sensor_fit, cam.data.shift_x, cam.data.shift_y = old_cam
    scene.render.filepath, scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.cycles.samples = old_render

print('\n'.join(paths))
return_value = paths
