import bpy
import json

CHAR_DX = 1.0  # CHAR_POS.x from place_character_lakeside.py
CHAR_DY = -7.0

mat = bpy.data.materials.get("皮肤")
tree = mat.node_tree

# 1. Report mesh world offset to confirm assumption
mesh = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
info = {}
if mesh is not None:
    verts = list(mesh.data.vertices)[::5000]
    ws = [mesh.matrix_world @ v.co for v in verts]
    info["mesh_world_sample"] = [[round(c, 4) for c in v] for v in ws[:5]]
if empty is not None:
    info["empty_loc"] = [round(v, 4) for v in empty.location]

# 2. Fix X-based masks for world offset
x_feather = tree.nodes.get("Codex Band Lift X Feather")
if x_feather is not None and x_feather.type == "MAP_RANGE":
    # inputs: 0 Value, 1 From Min, 2 From Max, 3 To Min, 4 To Max (float mode)
    fmin = x_feather.inputs[1].default_value
    fmax = x_feather.inputs[2].default_value
    # only shift if still at old studio values (avoid double-shift)
    if abs(float(fmin) - (-0.008)) < 1e-6:
        x_feather.inputs[1].default_value = float(fmin) + CHAR_DX
        x_feather.inputs[2].default_value = float(fmax) + CHAR_DX
        info["x_feather_shifted"] = [float(fmin), float(fmax), float(fmin)+CHAR_DX, float(fmax)+CHAR_DX]
    else:
        info["x_feather_already"] = [float(fmin), float(fmax)]

x_side = tree.nodes.get("Codex Baked Ring Character Right Side")
if x_side is not None and x_side.type == "MATH":
    thr = float(x_side.inputs[1].default_value)
    if abs(thr - (-0.02)) < 1e-6:
        x_side.inputs[1].default_value = thr + CHAR_DX
        info["x_side_shifted"] = [thr, thr+CHAR_DX]
    else:
        info["x_side_already"] = thr

mat["codex_band_lift_worldfix"] = f"dx_{CHAR_DX}"
bpy.ops.wm.save_mainfile()
print(json.dumps(info, ensure_ascii=False, indent=1))
