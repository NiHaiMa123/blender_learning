import bpy
import json

CHAR_POS = (1.0, -7.0, 0.0)
report = {}

# 1. unhide character
char_coll = bpy.data.collections.get("人物")
char_coll.hide_viewport = False
char_coll.hide_render = False
report["character_visible"] = True

# 2. link author character-light rig
rig = bpy.data.collections.get("人物灯光（b站搜三分仪打光教程）")
if rig is None:
    raise RuntimeError("rig collection not found")
if rig.name not in [c.name for c in bpy.context.scene.collection.children]:
    bpy.context.scene.collection.children.link(rig)
    report["rig_linked"] = True
else:
    report["rig_linked"] = False

# 3. attach loose rig members to the rig root (keep world transform)
root = bpy.data.objects.get("空物体.027")
for name in ("地面光.001", "脸.001", "身体.001"):
    o = bpy.data.objects.get(name)
    if o is not None and o.parent is None:
        o.parent = root
        o.matrix_parent_inverse = root.matrix_world.inverted()
report["rig_members_attached"] = True

# 4. move rig + character into place
root.location = CHAR_POS
empty = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311")
empty.location = CHAR_POS
empty.rotation_euler = (0.0, 0.0, 0.0)
report["char_pos"] = list(CHAR_POS)

# 5. park our studio lights (stay hidden in lakeside workspace)
studio = ["Key_Soft", "Rim_Cool", "Fill_Front", "Skin_Fill", "EyeLight",
          "Overhead_Soft", "Side_Fill_Left", "Back_Fill_Warm",
          "Metal_Strip_Key", "Metal_Strip_Rim", "Leg_Fill_Front",
          "Leg_Fill_Right", "Leg_Fill_Left", "Leg_Fill_Ring", "Practical_Warm"]
parked = []
for n in studio:
    o = bpy.data.objects.get(n)
    if o is not None:
        o.hide_render = True
        o.hide_viewport = True
        parked.append(n)
report["studio_lights_parked"] = len(parked)

bpy.ops.wm.save_mainfile()
report["saved"] = True

print(json.dumps(report, ensure_ascii=False, indent=1))
