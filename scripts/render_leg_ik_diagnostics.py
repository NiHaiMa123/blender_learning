import bpy
import json
import math
from mathutils import Matrix, Vector


ARMATURE_NAME = "卡提希娅_arm"
OUTPUT_DIR = r"D:\project\blender_learning\renders"


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


scene = bpy.context.scene
arm = bpy.data.objects[ARMATURE_NAME]
camera = scene.camera
original_basis = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
original_camera_matrix = camera.matrix_world.copy()
original_lens = camera.data.lens
original_settings = {
    "x": scene.render.resolution_x,
    "y": scene.render.resolution_y,
    "percentage": scene.render.resolution_percentage,
    "filepath": scene.render.filepath,
    "engine": scene.render.engine,
    "film_transparent": scene.render.film_transparent,
}
if scene.render.engine == "BLENDER_EEVEE":
    original_samples = scene.render.image_settings.file_format
else:
    original_samples = scene.cycles.samples

try:
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    if arm.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")
    bpy.context.view_layer.update()

    # Deliberately asymmetric, simultaneous foot-control test pose.
    moves = {
        "R": (Vector((-0.06, -0.18, 0.20)), math.radians(-16)),
        "L": (Vector((0.09, 0.05, 0.12)), math.radians(13)),
    }
    for side, (move, angle) in moves.items():
        foot = arm.pose.bones[f"足ＩＫ.{side}"]
        wm = arm.matrix_world @ foot.matrix
        foot.matrix = arm.matrix_world.inverted() @ (
            Matrix.Translation(move) @ wm @ Matrix.Rotation(angle, 4, "Z")
        )
    bpy.context.view_layer.update()

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False

    outputs = []
    views = [
        ("leg_ik_test_front.png", Vector((0.0, -4.0, 1.05)), Vector((0.0, 0.0, 0.82)), 58),
        ("leg_ik_test_three_quarter.png", Vector((2.8, -3.2, 1.10)), Vector((0.0, 0.0, 0.82)), 62),
    ]
    for filename, location, target, lens in views:
        camera.location = location
        camera.data.lens = lens
        look_at(camera, target)
        scene.render.filepath = OUTPUT_DIR + "\\" + filename
        bpy.ops.render.render(write_still=True)
        outputs.append(scene.render.filepath)

    print(json.dumps({"outputs": outputs}, ensure_ascii=False, indent=2))
finally:
    for pb in arm.pose.bones:
        if pb.name in original_basis:
            pb.matrix_basis = original_basis[pb.name].copy()
    bpy.context.view_layer.update()
    camera.matrix_world = original_camera_matrix
    camera.data.lens = original_lens
    scene.render.resolution_x = original_settings["x"]
    scene.render.resolution_y = original_settings["y"]
    scene.render.resolution_percentage = original_settings["percentage"]
    scene.render.filepath = original_settings["filepath"]
    scene.render.engine = original_settings["engine"]
    scene.render.film_transparent = original_settings["film_transparent"]
    if scene.render.engine != "BLENDER_EEVEE":
        scene.cycles.samples = original_samples
