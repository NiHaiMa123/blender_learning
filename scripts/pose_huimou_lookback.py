import bpy, json, math
from mathutils import Vector, Matrix

TURN_DEG = 150.0        # body turn about world Z (0 = facing camera)
SPINE_TWIST = 10.0      # 上半身2 yaw (world Z)
NECK_TWIST = 35.0       # 首 yaw
HEAD_TWIST = 90.0       # 頭 yaw -> face ends ~30deg off camera axis
LEAN_DEG = -4.0         # 上半身 forward lean (world X)
ARM_SWING = 18.0        # contralateral arm swing (world X)
ELBOW_BEND = 12.0
STRIDE = 0.13           # foot Y offset, keep Z=0 for contact

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
         "腕.L", "腕.R", "ひじ.L", "ひじ.R",
         "足ＩＫ.L", "足ＩＫ.R"]
for n in TOUCH:
    pb = pbones.get(n)
    if pb is not None:
        pb.matrix_basis.identity()
bpy.context.view_layer.update()


def rotate_global(name, axis, degrees):
    pb = pbones[name]
    bpy.context.view_layer.update()
    pivot = pb.head.copy()
    rot = Matrix.Rotation(math.radians(degrees), 4, Vector(axis))
    pb.matrix = Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot) @ pb.matrix
    bpy.context.view_layer.update()


def translate_pose(name, delta):
    pb = pbones[name]
    bpy.context.view_layer.update()
    m = pb.matrix.copy()
    m.translation += Vector(delta)
    pb.matrix = m
    bpy.context.view_layer.update()


# 1. whole-body turn (rigid, keeps internal pose; lights unaffected)
empty.rotation_euler = (0.0, 0.0, math.radians(TURN_DEG))
rep["empty_yaw"] = TURN_DEG

# 2. torso: lean + distributed look-back twist
rotate_global("上半身", (1, 0, 0), LEAN_DEG)
rotate_global("上半身2", (0, 0, 1), SPINE_TWIST)
rotate_global("首", (0, 0, 1), NECK_TWIST)
rotate_global("頭", (0, 0, 1), HEAD_TWIST)

# 3. walk: contralateral swing, left leg forward
translate_pose("足ＩＫ.L", (0.0, STRIDE, 0.0))
translate_pose("足ＩＫ.R", (0.0, -STRIDE, 0.0))
rotate_global("腕.R", (1, 0, 0), ARM_SWING)
rotate_global("腕.L", (1, 0, 0), -ARM_SWING)
rotate_global("ひじ.R", (1, 0, 0), ELBOW_BEND)
rotate_global("ひじ.L", (1, 0, 0), ELBOW_BEND)
bpy.context.view_layer.update()

# 4. mirror-aware band-lift X mask: bracket whichever world-X side the
#    anatomical right knee ended up on (turn flips sides)
kR = (arm.matrix_world @ pbones["ひざ.R"].head).x if "ひざ.R" in pbones else None
kL = (arm.matrix_world @ pbones["ひざ.L"].head).x if "ひざ.L" in pbones else None
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

arm["codex_huimou"] = f"turn{TURN_DEG}_stride{STRIDE}"
bpy.ops.wm.save_mainfile()
print(json.dumps(rep, ensure_ascii=False, indent=1))
