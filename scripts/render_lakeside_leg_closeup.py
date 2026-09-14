import bpy, os
from mathutils import Vector
scene = bpy.context.scene
cam = next((o for o in bpy.data.objects if o.type=="CAMERA" and o.data and o.data.name=="摄像机"), None)
old_loc = cam.location.copy()
old_rot_mode = cam.rotation_mode
old_quat = cam.rotation_quaternion.copy()
old_euler = cam.rotation_euler.copy()
old_lens = cam.data.lens
old_dof = (cam.data.dof.use_dof, cam.data.dof.focus_distance,
           cam.data.dof.aperture_fstop)
cam.data.dof.use_dof = False
old_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath)
old_samples = (scene.cycles.samples, scene.cycles.use_denoising)
old_cam = scene.camera
old_world = scene.world

# thigh world approx: char at (1.0,-7.0,0) + local (-0.08,0,0.7)
target = Vector((0.92, -7.0, 0.70))
cam.location = Vector((0.95, -8.3, 0.78))
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = (target - cam.location).to_track_quat("-Z", "Y")
cam.data.lens = 85.0
scene.camera = cam
w = bpy.data.worlds.get("World.002")
if w: scene.world = w
scene.render.engine = "CYCLES"
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1920, 1080, 100
scene.cycles.samples = 64
scene.cycles.use_denoising = True
out = r"D:\project\blender_learning\renders\_preview_right_leg_uv_1080p\leg_closeup_check.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)

cam.location = old_loc
cam.rotation_mode = "QUATERNION"
cam.rotation_quaternion = old_quat
cam.rotation_mode = old_rot_mode
if old_rot_mode != "QUATERNION":
    cam.rotation_euler = old_euler
cam.data.lens = old_lens
cam.data.dof.use_dof, cam.data.dof.focus_distance, cam.data.dof.aperture_fstop = old_dof
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage, scene.render.filepath = old_res
scene.cycles.samples, scene.cycles.use_denoising = old_samples
scene.camera = old_cam
scene.world = old_world
print(f"leg closeup done {out}")
