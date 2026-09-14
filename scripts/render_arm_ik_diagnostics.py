import bpy
import json
import math
from mathutils import Matrix, Vector


arm = bpy.data.objects["卡提希娅_arm"]
scene = bpy.context.scene
camera = scene.camera
output_dir = r"D:\project\blender_learning\renders"

original_basis = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
camera_matrix = camera.matrix_world.copy()
camera_lens = camera.data.lens
settings = {
    "engine": scene.render.engine,
    "x": scene.render.resolution_x,
    "y": scene.render.resolution_y,
    "percentage": scene.render.resolution_percentage,
    "filepath": scene.render.filepath,
}

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

try:
    if arm.mode != "POSE":
        bpy.context.view_layer.objects.active = arm
        arm.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")

    moves = {
        "R": (Vector((0.16, -0.14, 0.16)), math.radians(-22)),
        "L": (Vector((-0.13, -0.11, 0.10)), math.radians(18)),
    }
    for side, (offset, angle) in moves.items():
        hand = arm.pose.bones[f"手部IK.{side}"]
        matrix = hand.matrix.copy()
        matrix.translation += offset
        pos = matrix.translation.copy()
        hand.matrix = Matrix.Translation(pos) @ Matrix.Rotation(angle, 4, "Z") @ Matrix.Translation(-pos) @ matrix
    bpy.context.view_layer.update()

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 800
    scene.render.resolution_y = 650
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"

    outputs = []
    views = [
        ("arm_ik_test_front.png", Vector((0.0, -3.2, 1.30)), Vector((0.0, 0.0, 1.22)), 68),
        ("arm_ik_test_three_quarter.png", Vector((2.4, -2.6, 1.35)), Vector((0.0, 0.0, 1.20)), 72),
    ]
    for filename, location, target, lens in views:
        camera.location = location
        camera.data.lens = lens
        look_at(camera, target)
        scene.render.filepath = output_dir + "\\" + filename
        bpy.ops.render.render(write_still=True)
        outputs.append(scene.render.filepath)
    print(json.dumps({"outputs": outputs}, ensure_ascii=False, indent=2))
finally:
    for name, basis in original_basis.items():
        arm.pose.bones[name].matrix_basis = basis.copy()
    bpy.context.view_layer.update()
    camera.matrix_world = camera_matrix
    camera.data.lens = camera_lens
    scene.render.engine = settings["engine"]
    scene.render.resolution_x = settings["x"]
    scene.render.resolution_y = settings["y"]
    scene.render.resolution_percentage = settings["percentage"]
    scene.render.filepath = settings["filepath"]
