import bpy, json, math
from mathutils import Vector, Matrix

TURN_DEG = 235.0         # body turned 75° to her left from 160°
SPINE_TWIST = 10.0
NECK_TWIST = 25.0
HEAD_TWIST = 55.0       # head total yaw 90° — glance, not stare
HEAD_ROLL = 30.0      # character-left roll around the current facing axis
HEAD_PITCH = 40.0      # keep the face visible in the current look-back direction

rep = {}
empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
arm = next((o for o in bpy.data.objects
            if o.type == "ARMATURE" and o.parent is not None
            and o.parent.name == empty.name), None)
if arm is None:
    raise RuntimeError("character armature not found")
pbones = arm.pose.bones
rep["arm"] = arm.name

TOUCH = ["下半身", "上半身", "上半身1", "上半身2", "首", "頭",
         "肩.L", "肩.R", "腕.L", "腕.R", "ひじ.L", "ひじ.R",
         "手首.L", "手首.R", "足ＩＫ.L", "足ＩＫ.R",
         "つま先ＩＫ.L", "つま先ＩＫ.R"]
for n in TOUCH:
    pb = pbones.get(n)
    if pb is not None:
        pb.matrix_basis.identity()
for pb in pbones:
    if "指" in pb.name:
        pb.matrix_basis.identity()
bpy.context.view_layer.update()


def rotate_global(name, axis, degrees):
    pb = pbones[name]
    bpy.context.view_layer.update()
    pivot = pb.head.copy()
    rot = Matrix.Rotation(math.radians(degrees), 4, Vector(axis))
    pb.matrix = Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot) @ pb.matrix
    bpy.context.view_layer.update()


def aim_world(name, world_target):
    """Point bone head->tail at a world-space target (robust to empty yaw)."""
    pb = pbones[name]
    bpy.context.view_layer.update()
    inv = arm.matrix_world.inverted()
    lt = inv @ Vector(world_target)
    head = pb.head.copy()
    current = pb.tail - head
    desired = lt - head
    if current.length < 1e-6 or desired.length < 1e-6:
        return
    rot = current.normalized().rotation_difference(desired.normalized()).to_matrix().to_4x4()
    pb.matrix = Matrix.Translation(head) @ rot @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()


def world_point(pb):
    return arm.matrix_world @ pb.head


def aim_straight_arms_to_common_point():
    """Place both forearm tails at one shared clasp point with straight elbows."""
    upper = {side: pbones[f"腕.{side}"] for side in ("R", "L")}
    fore = {side: pbones[f"ひじ.{side}"] for side in ("R", "L")}
    shoulder = {side: world_point(upper[side]) for side in ("R", "L")}
    lengths = {
        side: upper[side].length + fore[side].length
        for side in ("R", "L")
    }
    midpoint = (shoulder["R"] + shoulder["L"]) * 0.5
    shoulder_delta = shoulder["L"] - shoulder["R"]
    lateral = shoulder_delta.normalized()
    back = (empty.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
    # Rotate the straight-arm direction a further 25° toward the back.
    base_back = 0.20
    base_down = 0.38
    arm_radius = math.sqrt(base_back * base_back + base_down * base_down)
    arm_angle = math.atan2(base_back, base_down) + math.radians(25.0)
    desired = back * (arm_radius * math.sin(arm_angle))
    desired += Vector((0.0, 0.0, -arm_radius * math.cos(arm_angle)))
    desired -= lateral * desired.dot(lateral)
    radius = (lengths["R"] + lengths["L"]) * 0.5
    half_span = shoulder_delta.length * 0.5
    desired_len = max(0.05, math.sqrt(max(0.01, radius * radius - half_span * half_span)))
    hand_point = midpoint + desired.normalized() * desired_len
    rep["clasp_world"] = [round(float(v), 4) for v in hand_point]
    rep["arm_lengths"] = {side: round(float(lengths[side]), 4) for side in ("R", "L")}

    # Keep each wrist on its own anatomical side; the previous crossed targets
    # made the forearms overlap in the render.
    cross_offset = 0.025
    hand_targets = {
        "R": hand_point - lateral * cross_offset,
        "L": hand_point + lateral * cross_offset,
    }
    rep["cross_offset"] = cross_offset
    for side in ("R", "L"):
        direction = (hand_targets[side] - shoulder[side]).normalized()
        elbow_point = shoulder[side] + direction * upper[side].length
        aim_world(f"腕.{side}", elbow_point)
        aim_world(f"ひじ.{side}", hand_targets[side])
    bpy.context.view_layer.update()


# 1. body turn, upright torso
empty.rotation_euler = (0.0, 0.0, math.radians(TURN_DEG))
rep["empty_yaw"] = TURN_DEG

# 2. head: distributed look-back + shy tilt
# The pose matrix is in armature-local space. Local +X is the pitch axis;
# positive rotation sends the torso toward the character's local -Y front.
rotate_global("上半身", (1.0, 0.0, 0.0), 30.0)
rotate_global("上半身2", (0, 0, 1), SPINE_TWIST)
rotate_global("首", (0, 0, 1), NECK_TWIST)
rotate_global("頭", (0, 0, 1), HEAD_TWIST)
rotate_global("頭", (0, 1, 0), HEAD_ROLL)
rotate_global("頭", (1, 0, 0), HEAD_PITCH)

# 3. straight arms behind back; wrists cross into a clasped-fist greeting
aim_straight_arms_to_common_point()
# Turn each wrist outward without changing the straight arm paths.
rotate_global("手首.L", (0.0, 0.0, 1.0), 10.0)
rotate_global("手首.R", (0.0, 0.0, 1.0), -10.0)
for side, sign in (("R", -1.0), ("L", 1.0)):
    # Normal open hand: clear the temporary fist curl and keep bind-pose fingers.
    for prefix, joints in (("人指", (("１", 0.0), ("２", 0.0), ("３", 0.0), ("３先", 0.0))),
                           ("中指", (("１", 0.0), ("２", 0.0), ("３", 0.0), ("３先", 0.0))),
                           ("薬指", (("１", 0.0), ("２", 0.0), ("３", 0.0), ("３先", 0.0))),
                           ("小指", (("１", 0.0), ("２", 0.0), ("３", 0.0), ("３先", 0.0))),
                           ("親指", (("０", 0.0), ("１", 0.0), ("２", 0.0), ("２先", 0.0)))):
        for suffix, curl in joints:
            pb = pbones.get(f"{prefix}{suffix}.{side}")
            if pb is not None:
                rotate_global(pb.name, (0, 1, 0), sign * curl)
bpy.context.view_layer.update()

# legs stay at bind (feet together, grounded); record knee side for mask
kR = (arm.matrix_world @ pbones["ひざ.R"].head).x
kL = (arm.matrix_world @ pbones["ひざ.L"].head).x
rep["knee_world_x"] = {"R": round(float(kR), 4), "L": round(float(kL), 4)}
mat = bpy.data.materials.get("皮肤")
tree = mat.node_tree
x_feather = tree.nodes.get("Codex Band Lift X Feather")
x_side = tree.nodes.get("Codex Baked Ring Character Right Side")
mid = (float(kR) + float(kL)) / 2.0
if float(kR) > mid:
    x_feather.inputs[1].default_value = mid - 0.002
    x_feather.inputs[2].default_value = mid + 0.005
    x_feather.inputs[3].default_value = 0.0
    x_feather.inputs[4].default_value = 1.0
    x_side.operation = "GREATER_THAN"
    x_side.inputs[1].default_value = mid
    rep["mask"] = {"side": "right_on_plusX", "mid": round(mid, 4)}
else:
    x_feather.inputs[1].default_value = mid - 0.005
    x_feather.inputs[2].default_value = mid + 0.002
    x_feather.inputs[3].default_value = 1.0
    x_feather.inputs[4].default_value = 0.0
    x_side.operation = "LESS_THAN"
    x_side.inputs[1].default_value = mid
    rep["mask"] = {"side": "right_on_minusX", "mid": round(mid, 4)}

arm["codex_reflook"] = f"turn{TURN_DEG}"
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
