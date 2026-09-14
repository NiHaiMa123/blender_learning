import bpy

GAIN_R, GAIN_G, GAIN_B = 1.02, 1.32, 1.36
# Second stage: pull lifted band skin toward the surrounding tone so baked
# contact tint / lace lines (which multiply alone cannot erase) fade out.
# Pixels already near the target barely move, so detail loss is minimal.
TARGET_R, TARGET_G, TARGET_B = 0.860, 0.767, 0.778
REPLACE_K = 1.00
# Full-strength band in object-space Z, feathered soft edges (smoothstep).
Z_FULL_LO, Z_FEATHER_LO = 0.625, 0.585
Z_FULL_HI, Z_FEATHER_HI = 0.765, 0.795

mat = bpy.data.materials.get("皮肤")
if mat is None or not mat.use_nodes or not mat.node_tree:
    raise RuntimeError("Skin material not found")
tree = mat.node_tree
texture = tree.nodes.get("Skin Base Texture")
balance = tree.nodes.get("Skin Color Balance")
position = tree.nodes.get("Codex Baked Ring Position")
final_mask = tree.nodes.get("Codex Baked Ring Final Mask")
if texture is None or balance is None or position is None or final_mask is None:
    raise RuntimeError("Required skin nodes not found")

for node in list(tree.nodes):
    if node.name.startswith("Codex Band Lift"):
        tree.nodes.remove(node)


def math(op, name, x, y, v1=None):
    n = tree.nodes.new("ShaderNodeMath")
    n.name = name
    n.operation = op
    n.location = (x, y)
    if v1 is not None:
        n.inputs[1].default_value = v1
    return n


def map_range(name, x, y, from_min, from_max, to_min=0.0, to_max=1.0):
    n = tree.nodes.new("ShaderNodeMapRange")
    n.name = name
    n.location = (x, y)
    n.data_type = "FLOAT"
    n.interpolation_type = "SMOOTHSTEP"
    n.clamp = True
    value_sock = n.inputs[0]
    from_min_sock = n.inputs[1]
    from_max_sock = n.inputs[2]
    to_min_sock = n.inputs[3]
    to_max_sock = n.inputs[4]
    value_sock.name  # keep socket order stable across versions
    from_min_sock.default_value = from_min
    from_max_sock.default_value = from_max
    to_min_sock.default_value = to_min
    to_max_sock.default_value = to_max
    return n


sep = tree.nodes.new("ShaderNodeSeparateColor")
sep.name = "Codex Band Lift Separate"
sep.mode = "RGB"
sep.location = (-320, -60)

gain_r = math("MULTIPLY", "Codex Band Lift Gain R", -100, -20, GAIN_R)
gain_g = math("MULTIPLY", "Codex Band Lift Gain G", -100, -100, GAIN_G)
gain_b = math("MULTIPLY", "Codex Band Lift Gain B", -100, -180, GAIN_B)

comb = tree.nodes.new("ShaderNodeCombineColor")
comb.name = "Codex Band Lift Combine"
comb.mode = "RGB"
comb.location = (120, -100)

z_in = map_range("Codex Band Lift Z In", 120, -560, Z_FEATHER_LO, Z_FULL_LO)
z_out = map_range("Codex Band Lift Z Out", 120, -680, Z_FULL_HI, Z_FEATHER_HI, 1.0, 0.0)
x_feather = map_range("Codex Band Lift X Feather", 120, -800, -0.008, -0.001, 1.0, 0.0)

geo_z = math("MULTIPLY", "Codex Band Lift Geometry Z", 330, -600)
geo_all = math("MULTIPLY", "Codex Band Lift Geometry All", 500, -620)
not_gold = math("SUBTRACT", "Codex Band Lift Not Gold", 500, -720)
not_gold.inputs[0].default_value = 1.0
band_mask = math("MULTIPLY", "Codex Band Lift Mask", 670, -660)

mix = tree.nodes.new("ShaderNodeMixRGB")
mix.name = "Codex Band Lift Mix"
mix.label = "Band skin lift (keep gold ring)"
mix.blend_type = "MIX"
mix.location = (-80, 200)

tree.links.new(texture.outputs["Color"], sep.inputs["Color"])
tree.links.new(sep.outputs[0], gain_r.inputs[0])
tree.links.new(sep.outputs[1], gain_g.inputs[0])
tree.links.new(sep.outputs[2], gain_b.inputs[0])
tree.links.new(gain_r.outputs[0], comb.inputs[0])
tree.links.new(gain_g.outputs[0], comb.inputs[1])
tree.links.new(gain_b.outputs[0], comb.inputs[2])

tree.links.new(position.outputs[2], z_in.inputs[0])
tree.links.new(position.outputs[2], z_out.inputs[0])
tree.links.new(position.outputs[0], x_feather.inputs[0])
tree.links.new(z_in.outputs[0], geo_z.inputs[0])
tree.links.new(z_out.outputs[0], geo_z.inputs[1])
tree.links.new(geo_z.outputs[0], geo_all.inputs[0])
tree.links.new(x_feather.outputs[0], geo_all.inputs[1])
tree.links.new(final_mask.outputs[0], not_gold.inputs[1])
# Ring geometry is hidden (transparent) and the baked overlay is bypassed,
# so flatten the whole band rectangle INCLUDING baked gold paint.
tree.links.new(geo_all.outputs[0], band_mask.inputs[0])
tree.links.new(geo_all.outputs[0], band_mask.inputs[1])

tree.links.new(texture.outputs["Color"], mix.inputs[1])
tree.links.new(comb.outputs["Color"], mix.inputs[2])
tree.links.new(band_mask.outputs[0], mix.inputs[0])

# Second stage: flatten lifted band skin toward surrounding tone.
target = tree.nodes.new("ShaderNodeCombineColor")
target.name = "Codex Band Lift Target"
target.mode = "RGB"
target.location = (120, -260)
target.inputs[0].default_value = TARGET_R
target.inputs[1].default_value = TARGET_G
target.inputs[2].default_value = TARGET_B

replace_fac = math("MULTIPLY", "Codex Band Lift Replace Fac", 670, -780, REPLACE_K)
tree.links.new(band_mask.outputs[0], replace_fac.inputs[0])

replace = tree.nodes.new("ShaderNodeMixRGB")
replace.name = "Codex Band Lift Replace"
replace.label = "Baked tint flatten toward surround"
replace.blend_type = "MIX"
replace.location = (330, -40)
tree.links.new(comb.outputs["Color"], replace.inputs[1])
tree.links.new(target.outputs["Color"], replace.inputs[2])
tree.links.new(replace_fac.outputs[0], replace.inputs[0])

for link in list(tree.links):
    if link.from_node == comb and link.to_node == mix:
        tree.links.remove(link)
tree.links.new(replace.outputs["Color"], mix.inputs[2])

for link in list(tree.links):
    if link.to_node == balance and link.to_socket.name == "Color":
        tree.links.remove(link)
tree.links.new(mix.outputs["Color"], balance.inputs["Color"])

mat["codex_band_lift"] = (
    f"gain_{GAIN_R}_{GAIN_G}_{GAIN_B}_"
    f"zfull_{Z_FULL_LO}_{Z_FULL_HI}_feather_{Z_FEATHER_LO}_{Z_FEATHER_HI}"
)
print(f"Applied band lift gain=({GAIN_R},{GAIN_G},{GAIN_B})")
