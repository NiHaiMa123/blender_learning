import bpy
import math
from mathutils import Vector, Matrix

arm = bpy.data.objects["卡提希娅_arm"]
pbones = arm.pose.bones


def reset(name):
    pb = pbones.get(name)
    if pb:
        pb.matrix_basis.identity()


def rotate_global(name, axis, degrees):
    pb = pbones[name]
    bpy.context.view_layer.update()
    pivot = pb.head.copy()
    rot = Matrix.Rotation(math.radians(degrees), 4, Vector(axis))
    pb.matrix = Matrix.Translation(pivot) @ rot @ Matrix.Translation(-pivot) @ pb.matrix
    bpy.context.view_layer.update()


def aim(name, target):
    pb = pbones[name]
    bpy.context.view_layer.update()
    head = pb.head.copy()
    current = pb.tail - head
    desired = Vector(target) - head
    if current.length < 1e-6 or desired.length < 1e-6:
        return
    rot = current.normalized().rotation_difference(desired.normalized()).to_matrix().to_4x4()
    pb.matrix = Matrix.Translation(head) @ rot @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()


def translate_pose(name, delta):
    pb = pbones[name]
    bpy.context.view_layer.update()
    matrix = pb.matrix.copy()
    matrix.translation += Vector(delta)
    pb.matrix = matrix
    bpy.context.view_layer.update()


controls = [
    "センター", "センター2", "グルーブ", "グルーブ2", "腰", "下半身",
    "上半身", "上半身1", "上半身2", "首", "頭",
    "肩.R", "腕.R", "ひじ.R", "手首.R",
    "肩.L", "腕.L", "ひじ.L", "手首.L",
    "足ＩＫ.R", "つま先ＩＫ.R", "足ＩＫ.L", "つま先ＩＫ.L",
]
for bone_name in controls:
    reset(bone_name)
bpy.context.view_layer.update()

# Elegant S-curve through hips, chest, neck and head.
rotate_global("下半身", (0, 0, 1), -7.0)
rotate_global("腰", (1, 0, 0), 2.5)
rotate_global("上半身", (0, 0, 1), 6.0)
rotate_global("上半身1", (0, 1, 0), -3.0)
rotate_global("上半身2", (0, 0, 1), 7.0)
rotate_global("首", (0, 0, 1), -4.0)
rotate_global("頭", (0, 1, 0), -8.0)
rotate_global("頭", (0, 0, 1), -5.0)

# Anatomical right arm: elbow opens sideways, wrist rises beside the cheek.
aim("腕.R", (-0.36, -0.10, 1.39))
aim("ひじ.R", (-0.22, -0.19, 1.45))
rotate_global("手首.R", (0, 1, 0), -20.0)
rotate_global("手首.R", (0, 0, 1), 18.0)

# Anatomical left arm: graceful outward presentation with a soft elbow bend.
aim("腕.L", (0.37, -0.07, 1.28))
aim("ひじ.L", (0.62, -0.13, 1.36))
rotate_global("手首.L", (1, 0, 0), 68.0)
rotate_global("手首.L", (0, 1, 0), -42.0)

# Crossed-leg silhouette: right foot slightly back/inside, left foot forward.
translate_pose("足ＩＫ.R", (0.035, 0.07, 0.012))
translate_pose("足ＩＫ.L", (-0.025, -0.11, 0.0))
rotate_global("足ＩＫ.R", (0, 0, 1), -6.0)
rotate_global("足ＩＫ.L", (0, 0, 1), 5.0)

# Relaxed open fingers. Curl only the inner joints very slightly.
for side, sign in (("R", -1.0), ("L", 1.0)):
    for prefix, curl in (("人指", 5.0), ("中指", 7.0), ("薬指", 9.0), ("小指", 11.0)):
        for index in (1, 2):
            name = f"{prefix}{index}.{side}"
            if name in pbones:
                rotate_global(name, (0, 1, 0), sign * curl)

bpy.context.view_layer.update()
print("Applied reference-inspired static pose")
for name in ("手首.R", "手首.L", "足ＩＫ.R", "足ＩＫ.L"):
    pb = pbones[name]
    print(name, tuple(round(float(v), 4) for v in pb.head))
