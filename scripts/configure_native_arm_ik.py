import bpy
import json
import math
import os
from mathutils import Matrix, Vector


ARMATURE_NAME = "卡提希娅_arm"
OUTPUT = r"D:\project\blender_learning\renders\carthya_character_only_keyframing.blend"
BACKUP = r"D:\project\blender_learning\renders\before_native_arm_ik.blend"
COLLECTION_NAME = "【主控】手部IK"

arm = bpy.data.objects[ARMATURE_NAME]
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=BACKUP, copy=True, check_existing=False)

for obj in bpy.context.view_layer.objects:
    obj.select_set(False)
arm.hide_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if arm.mode != "POSE":
    bpy.ops.object.mode_set(mode="POSE")

# Preserve the user's current pose and evaluated arm state exactly.
pose_snapshot = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
baseline = {
    name: arm.pose.bones[name].matrix.copy()
    for side in ("R", "L")
    for name in (f"腕.{side}", f"腕捩.{side}", f"ひじ.{side}", f"手捩.{side}", f"手首.{side}")
}
baseline.update({name: arm.pose.bones[name].matrix.copy() for name in ("上半身", "上半身2", "首", "下半身")})
current_wrist_matrices = {side: arm.pose.bones[f"手首.{side}"].matrix.copy() for side in ("R", "L")}

def current_pole_position(side):
    shoulder = arm.pose.bones[f"腕.{side}"].head.copy()
    elbow = arm.pose.bones[f"ひじ.{side}"].head.copy()
    wrist = arm.pose.bones[f"手首.{side}"].head.copy()
    axis = wrist - shoulder
    if axis.length < 1e-8:
        return elbow + Vector((0.0, -0.36, 0.0))
    axis.normalize()
    bend = elbow - shoulder
    bend -= axis * bend.dot(axis)
    if bend.length < 0.015:
        bend = Vector((0.0, -1.0, 0.0))
        bend -= axis * bend.dot(axis)
    if bend.length < 1e-8:
        bend = Vector((0.0, 0.0, 1.0))
    return elbow + bend.normalized() * 0.36

current_poles = {side: current_pole_position(side) for side in ("R", "L")}

bpy.ops.object.mode_set(mode="EDIT")
edit_bones = arm.data.edit_bones
root = edit_bones.get("全ての親")
if root is None:
    raise RuntimeError("Global root control is missing")

created = []
for side in ("R", "L"):
    wrist = edit_bones[f"手首.{side}"]
    hand_name = f"手部IK.{side}"
    hand = edit_bones.get(hand_name)
    if hand is None:
        hand = edit_bones.new(hand_name)
        created.append(hand_name)
    direction = wrist.tail - wrist.head
    if direction.length < 1e-8:
        direction = Vector((0.0, 0.0, 1.0))
    hand.head = wrist.head
    hand.tail = wrist.head + direction.normalized() * 0.12
    hand.parent = root
    hand.use_connect = False
    hand.use_deform = False

    elbow = edit_bones[f"ひじ.{side}"]
    pole_name = f"手肘朝向.{side}"
    pole = edit_bones.get(pole_name)
    if pole is None:
        pole = edit_bones.new(pole_name)
        created.append(pole_name)
    pole.head = elbow.head + Vector((0.0, -0.36, 0.0))
    pole.tail = pole.head + Vector((0.0, 0.0, 0.11))
    pole.parent = root
    pole.use_connect = False
    pole.use_deform = False

bpy.ops.object.mode_set(mode="POSE")

collection = arm.data.collections.get(COLLECTION_NAME)
if collection is None:
    collection = arm.data.collections.new(COLLECTION_NAME)
collection.is_visible = True

for side in ("R", "L"):
    hand_name = f"手部IK.{side}"
    pole_name = f"手肘朝向.{side}"
    collection.assign(arm.data.bones[hand_name])
    collection.assign(arm.data.bones[pole_name])

    hand_pb = arm.pose.bones[hand_name]
    hand_pb.rotation_mode = "QUATERNION"
    hand_pb.lock_location = (False, False, False)
    hand_pb.lock_rotation = (False, False, False)
    hand_pb.lock_rotation_w = False
    hand_pb.lock_scale = (True, True, True)

    pole_pb = arm.pose.bones[pole_name]
    pole_pb.rotation_mode = "QUATERNION"
    pole_pb.lock_location = (False, False, False)
    pole_pb.lock_rotation = (True, True, True)
    pole_pb.lock_rotation_w = True
    pole_pb.lock_scale = (True, True, True)

# Restore all pre-edit user transforms, then place controls on the currently posed wrists/elbows.
for name, basis in pose_snapshot.items():
    if name in arm.pose.bones:
        arm.pose.bones[name].matrix_basis = basis.copy()
bpy.context.view_layer.update()

for side in ("R", "L"):
    arm.pose.bones[f"手部IK.{side}"].matrix = current_wrist_matrices[side].copy()
    pole = arm.pose.bones[f"手肘朝向.{side}"]
    pole_matrix = pole.matrix.copy()
    pole_matrix.translation = current_poles[side]
    pole.matrix = pole_matrix
bpy.context.view_layer.update()

ik_constraints = {}
rotation_constraints = {}
for side in ("R", "L"):
    elbow = arm.pose.bones[f"ひじ.{side}"]
    ik_name = "原生手臂IK（含手肘朝向）"
    candidates = [c for c in elbow.constraints if c.type == "IK" and c.name == ik_name]
    ik = candidates[0] if candidates else elbow.constraints.new("IK")
    ik.name = ik_name
    ik.target = arm
    ik.subtarget = f"手部IK.{side}"
    ik.pole_target = arm
    ik.pole_subtarget = f"手肘朝向.{side}"
    ik.chain_count = 3  # Includes the existing upper-arm twist helper between arm and elbow.
    ik.iterations = 200
    ik.influence = 1.0
    ik.mute = False
    if hasattr(ik, "use_rotation"):
        ik.use_rotation = False
    ik_constraints[side] = ik

    # Prevent the existing twist helper from being treated as another bending joint.
    twist = arm.pose.bones[f"腕捩.{side}"]
    twist.lock_ik_x = True
    twist.lock_ik_y = True
    twist.lock_ik_z = True

    wrist = arm.pose.bones[f"手首.{side}"]
    copy_name = "手腕跟随手部IK旋转"
    copies = [c for c in wrist.constraints if c.type == "COPY_ROTATION" and c.name == copy_name]
    copy = copies[0] if copies else wrist.constraints.new("COPY_ROTATION")
    copy.name = copy_name
    copy.target = arm
    copy.subtarget = f"手部IK.{side}"
    copy.target_space = "POSE"
    copy.owner_space = "POSE"
    copy.mix_mode = "REPLACE"
    copy.influence = 1.0
    copy.mute = False
    rotation_constraints[side] = copy

def matrix_error(a, b):
    return sum((a[r][c] - b[r][c]) ** 2 for r in range(4) for c in range(4))

# Bone roll differs on the two imported sides. Find the pole angle that preserves the user's pose.
pole_angles = {}
for side in ("R", "L"):
    ik = ik_constraints[side]
    names = (f"腕.{side}", f"腕捩.{side}", f"ひじ.{side}", f"手首.{side}")
    best = None
    for degree in range(-180, 181, 2):
        ik.pole_angle = math.radians(degree)
        bpy.context.view_layer.update()
        error = sum(matrix_error(arm.pose.bones[name].matrix, baseline[name]) for name in names)
        if best is None or error < best[0]:
            best = (error, degree)
    ik.pole_angle = math.radians(best[1])
    bpy.context.view_layer.update()
    pole_angles[side] = {"degrees": best[1], "pose_error": best[0]}

def max_matrix_delta(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))

def rotation_alignment(a, b):
    qa = a.to_quaternion()
    qb = b.to_quaternion()
    return abs(qa.dot(qb))

# New post-configuration baseline is used to verify true left/right independence.
configured_basis = {pb.name: pb.matrix_basis.copy() for pb in arm.pose.bones}
bpy.context.view_layer.update()
configured_eval = {
    name: arm.pose.bones[name].matrix.copy()
    for side in ("R", "L")
    for name in (f"腕.{side}", f"腕捩.{side}", f"ひじ.{side}", f"手捩.{side}", f"手首.{side}")
}
configured_torso = {name: arm.pose.bones[name].matrix.copy() for name in ("上半身", "上半身2", "首", "下半身")}

def test_side(side, delta, degrees):
    for name, basis in configured_basis.items():
        arm.pose.bones[name].matrix_basis = basis.copy()
    bpy.context.view_layer.update()

    hand = arm.pose.bones[f"手部IK.{side}"]
    matrix = hand.matrix.copy()
    matrix.translation += Vector(delta)
    pos = matrix.translation.copy()
    rotation = Matrix.Rotation(math.radians(degrees), 4, "Z")
    matrix = Matrix.Translation(pos) @ rotation @ Matrix.Translation(-pos) @ matrix
    hand.matrix = matrix
    bpy.context.view_layer.update()

    upper = arm.pose.bones[f"腕.{side}"]
    elbow = arm.pose.bones[f"ひじ.{side}"]
    wrist = arm.pose.bones[f"手首.{side}"]
    pole = arm.pose.bones[f"手肘朝向.{side}"]
    shoulder_p = upper.head.copy()
    elbow_p = elbow.head.copy()
    wrist_p = wrist.head.copy()
    target_p = hand.head.copy()
    axis = wrist_p - shoulder_p
    projection = shoulder_p + axis * ((elbow_p - shoulder_p).dot(axis) / max(axis.length_squared, 1e-12))
    bend = elbow_p - projection
    pole_dir = pole.head - projection
    alignment = bend.normalized().dot(pole_dir.normalized()) if bend.length > 1e-8 and pole_dir.length > 1e-8 else 0.0

    other = "L" if side == "R" else "R"
    other_delta = max(
        max_matrix_delta(arm.pose.bones[f"{name}.{other}"].matrix, configured_eval[f"{name}.{other}"])
        for name in ("腕", "腕捩", "ひじ", "手捩", "手首")
    )
    torso_delta = max(max_matrix_delta(arm.pose.bones[n].matrix, configured_torso[n]) for n in configured_torso)
    return {
        "wrist_target_error": (wrist_p - target_p).length,
        "pole_alignment": alignment,
        "elbow_bend_amount": bend.length,
        "wrist_rotation_alignment": rotation_alignment(wrist.matrix, hand.matrix),
        "opposite_arm_delta": other_delta,
        "torso_delta": torso_delta,
    }

tests = {
    "R": test_side("R", (0.08, -0.13, 0.10), -22),
    "L": test_side("L", (-0.08, -0.12, 0.12), 20),
}

# Restore the starting configured pose and leave hand controls selected in Pose Mode.
for name, basis in configured_basis.items():
    arm.pose.bones[name].matrix_basis = basis.copy()
bpy.context.view_layer.update()
bpy.ops.pose.select_all(action="DESELECT")
for side in ("R", "L"):
    arm.pose.bones[f"手部IK.{side}"].select = True
arm.data.bones.active = arm.data.bones["手部IK.R"]

for area in bpy.context.window.screen.areas:
    area.tag_redraw()

bpy.ops.wm.save_as_mainfile(filepath=OUTPUT, copy=True, check_existing=False)
result = {
    "created": created,
    "collection": COLLECTION_NAME,
    "pole_angles": pole_angles,
    "tests": tests,
    "saved": OUTPUT,
    "backup": BACKUP,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
