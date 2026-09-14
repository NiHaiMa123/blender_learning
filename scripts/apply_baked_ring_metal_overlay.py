import bpy

material = bpy.data.materials.get("皮肤")
if material is None or not material.use_nodes or not material.node_tree:
    raise RuntimeError("Skin material not found")
tree = material.node_tree
texture = tree.nodes.get("Skin Base Texture")
skin_shader = tree.nodes.get("Skin Principled")
output = next((node for node in tree.nodes if node.type == "OUTPUT_MATERIAL"), None)
if texture is None or skin_shader is None or output is None:
    raise RuntimeError("Skin shader nodes not found")

for node in list(tree.nodes):
    if node.name.startswith("Codex Baked Ring"):
        tree.nodes.remove(node)

separate = tree.nodes.new("ShaderNodeSeparateColor")
separate.name = "Codex Baked Ring HSV"
separate.mode = "HSV"
separate.location = (-320, -280)

hue_subtract = tree.nodes.new("ShaderNodeMath")
hue_subtract.name = "Codex Baked Ring Hue Offset"
hue_subtract.operation = "SUBTRACT"
hue_subtract.inputs[1].default_value = 0.08
hue_subtract.location = (-100, -240)

hue_abs = tree.nodes.new("ShaderNodeMath")
hue_abs.name = "Codex Baked Ring Hue Distance"
hue_abs.operation = "ABSOLUTE"
hue_abs.location = (60, -240)

hue_mask = tree.nodes.new("ShaderNodeMath")
hue_mask.name = "Codex Baked Ring Hue Mask"
hue_mask.operation = "LESS_THAN"
hue_mask.inputs[1].default_value = 0.035
hue_mask.location = (220, -240)

sat_mask = tree.nodes.new("ShaderNodeMath")
sat_mask.name = "Codex Baked Ring Saturation Mask"
sat_mask.operation = "GREATER_THAN"
sat_mask.inputs[1].default_value = 0.40
sat_mask.location = (60, -340)

value_low = tree.nodes.new("ShaderNodeMath")
value_low.name = "Codex Baked Ring Value Min"
value_low.operation = "GREATER_THAN"
value_low.inputs[1].default_value = 0.12
value_low.location = (60, -440)

value_high = tree.nodes.new("ShaderNodeMath")
value_high.name = "Codex Baked Ring Value Max"
value_high.operation = "LESS_THAN"
value_high.inputs[1].default_value = 0.82
value_high.location = (60, -520)

geometry = tree.nodes.new("ShaderNodeNewGeometry")
geometry.name = "Codex Baked Ring Geometry"
geometry.location = (-320, -560)

position = tree.nodes.new("ShaderNodeSeparateXYZ")
position.name = "Codex Baked Ring Position"
position.location = (-100, -560)

x_mask = tree.nodes.new("ShaderNodeMath")
x_mask.name = "Codex Baked Ring Character Right Side"
x_mask.operation = "LESS_THAN"
x_mask.inputs[1].default_value = -0.02
x_mask.location = (60, -560)

z_min = tree.nodes.new("ShaderNodeMath")
z_min.name = "Codex Baked Ring Z Min"
z_min.operation = "GREATER_THAN"
z_min.inputs[1].default_value = 0.62
z_min.location = (60, -660)

z_max = tree.nodes.new("ShaderNodeMath")
z_max.name = "Codex Baked Ring Z Max"
z_max.operation = "LESS_THAN"
z_max.inputs[1].default_value = 0.78
z_max.location = (60, -760)

color_mask = tree.nodes.new("ShaderNodeMath")
color_mask.name = "Codex Baked Ring Color Mask"
color_mask.operation = "MULTIPLY"
color_mask.location = (400, -280)

color_mask_2 = tree.nodes.new("ShaderNodeMath")
color_mask_2.name = "Codex Baked Ring Color Mask 2"
color_mask_2.operation = "MULTIPLY"
color_mask_2.location = (560, -280)

geometry_mask = tree.nodes.new("ShaderNodeMath")
geometry_mask.name = "Codex Baked Ring Geometry Mask"
geometry_mask.operation = "MULTIPLY"
geometry_mask.location = (400, -560)

geometry_mask_2 = tree.nodes.new("ShaderNodeMath")
geometry_mask_2.name = "Codex Baked Ring Geometry Mask 2"
geometry_mask_2.operation = "MULTIPLY"
geometry_mask_2.location = (560, -560)

final_mask = tree.nodes.new("ShaderNodeMath")
final_mask.name = "Codex Baked Ring Final Mask"
final_mask.operation = "MULTIPLY"
final_mask.location = (730, -400)

combined_mask = tree.nodes.new("ShaderNodeMath")
combined_mask.name = "Codex Baked Ring Combined Mask"
combined_mask.operation = "MULTIPLY"
combined_mask.location = (900, -400)

tint = tree.nodes.new("ShaderNodeMixRGB")
tint.name = "Codex Baked Ring Gold Tint"
tint.label = "Baked ring warm gold"
tint.blend_type = "MIX"
tint.location = (720, 40)
tint.inputs[0].default_value = 0.40
tint.inputs[2].default_value = (0.95, 0.56, 0.12, 1.0)

metal = tree.nodes.new("ShaderNodeBsdfPrincipled")
metal.name = "Codex Baked Ring PBR Metal"
metal.label = "Baked skin ring -> metal"
metal.location = (960, 40)
metal.inputs["Metallic"].default_value = 0.94
metal.inputs["Roughness"].default_value = 0.18
metal.inputs["IOR"].default_value = 1.45
if metal.inputs.get("Specular IOR Level"):
    metal.inputs["Specular IOR Level"].default_value = 0.5
if metal.inputs.get("Coat Weight"):
    metal.inputs["Coat Weight"].default_value = 0.08
if metal.inputs.get("Coat Roughness"):
    metal.inputs["Coat Roughness"].default_value = 0.12

mix = tree.nodes.new("ShaderNodeMixShader")
mix.name = "Codex Baked Ring Mix"
mix.label = "Skin with baked ring metal overlay"
mix.location = (1240, 40)

tree.links.new(texture.outputs["Color"], separate.inputs["Color"])
tree.links.new(separate.outputs[0], hue_subtract.inputs[0])
tree.links.new(hue_subtract.outputs[0], hue_abs.inputs[0])
tree.links.new(hue_abs.outputs[0], hue_mask.inputs[0])
tree.links.new(separate.outputs[1], sat_mask.inputs[0])
tree.links.new(separate.outputs[2], value_low.inputs[0])
tree.links.new(separate.outputs[2], value_high.inputs[0])
tree.links.new(hue_mask.outputs[0], color_mask.inputs[0])
tree.links.new(sat_mask.outputs[0], color_mask.inputs[1])
tree.links.new(color_mask.outputs[0], color_mask_2.inputs[0])
tree.links.new(value_low.outputs[0], color_mask_2.inputs[1])
tree.links.new(color_mask_2.outputs[0], final_mask.inputs[0])
tree.links.new(value_high.outputs[0], final_mask.inputs[1])
tree.links.new(geometry.outputs["Position"], position.inputs[0])
tree.links.new(position.outputs[0], x_mask.inputs[0])
tree.links.new(position.outputs[2], z_min.inputs[0])
tree.links.new(position.outputs[2], z_max.inputs[0])
tree.links.new(x_mask.outputs[0], geometry_mask.inputs[0])
tree.links.new(z_min.outputs[0], geometry_mask.inputs[1])
tree.links.new(geometry_mask.outputs[0], geometry_mask_2.inputs[0])
tree.links.new(z_max.outputs[0], geometry_mask_2.inputs[1])
tree.links.new(final_mask.outputs[0], combined_mask.inputs[0])
tree.links.new(geometry_mask_2.outputs[0], combined_mask.inputs[1])
tree.links.new(combined_mask.outputs[0], mix.inputs[0])
tree.links.new(texture.outputs["Color"], tint.inputs[1])
tree.links.new(tint.outputs["Color"], metal.inputs["Base Color"])
tree.links.new(skin_shader.outputs["BSDF"], mix.inputs[1])
tree.links.new(metal.outputs["BSDF"], mix.inputs[2])

for link in list(tree.links):
    if link.to_node == output and link.to_socket.name == "Surface":
        tree.links.remove(link)
tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])
material["codex_baked_ring_metal_overlay"] = "hue_0.08_geometry_xneg_z0.62_0.78"
print("Applied baked ring metal overlay to skin shader")
