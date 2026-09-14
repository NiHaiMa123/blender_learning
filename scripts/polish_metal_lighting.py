import bpy
from mathutils import Vector


CHARACTER_TARGET = Vector((0.02, 0.18, 0.92))
FACE_TARGET = Vector((0.02, 0.18, 1.40))


def point_at(obj, target):
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (Vector(target) - obj.location).to_track_quat("-Z", "Y")


def set_input(node, name, value):
    socket = node.inputs.get(name)
    if socket is not None:
        socket.default_value = value


def rebuild_metal_material(name, roughness):
    material = bpy.data.materials.get(name)
    if not material or not material.use_nodes or not material.node_tree:
        return False
    tree = material.node_tree
    texture = tree.nodes.get("mmd_base_tex")
    output = next((node for node in tree.nodes if node.type == "OUTPUT_MATERIAL"), None)
    if texture is None or output is None:
        return False

    node_name = f"Codex Metal PBR {name}"
    bsdf = tree.nodes.get(node_name)
    if bsdf is None:
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.name = node_name
        bsdf.label = f"PBR metal: {name}"
        bsdf.location = (440, 80)
    else:
        for link in list(tree.links):
            if link.to_node == bsdf and link.to_socket.name == "Base Color":
                tree.links.remove(link)

    color_socket = texture.outputs.get("Color")
    base_socket = bsdf.inputs.get("Base Color")
    if color_socket and base_socket:
        tree.links.new(color_socket, base_socket)
    set_input(bsdf, "Metallic", 0.96)
    set_input(bsdf, "Roughness", roughness)
    set_input(bsdf, "IOR", 1.45)
    set_input(bsdf, "Specular IOR Level", 0.5)
    set_input(bsdf, "Coat Weight", 0.08)
    set_input(bsdf, "Coat Roughness", 0.12)

    for link in list(tree.links):
        if link.to_node == output and link.to_socket.name == "Surface":
            tree.links.remove(link)
    tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    material["codex_material_optimization"] = "v2_pbr_metal"
    material["codex_material_role"] = "metal"
    material.use_backface_culling = False
    return True


def apply_gold_texture_mask(name):
    material = bpy.data.materials.get(name)
    if not material or not material.use_nodes or not material.node_tree:
        return False
    tree = material.node_tree
    texture = tree.nodes.get("mmd_base_tex")
    shader = tree.nodes.get("mmd_shader")
    output = next((node for node in tree.nodes if node.type == "OUTPUT_MATERIAL"), None)
    if texture is None or shader is None or output is None or texture.image is None:
        return False

    for node in list(tree.nodes):
        if node.name.startswith("Codex Gold Mask") or node.name.startswith("Codex Gold PBR") or node.name.startswith("Codex Gold Mix"):
            tree.nodes.remove(node)

    separate = tree.nodes.new("ShaderNodeSeparateColor")
    separate.name = f"Codex Gold Mask HSV {name}"
    separate.mode = "HSV"
    separate.location = (-260, -300)

    subtract = tree.nodes.new("ShaderNodeMath")
    subtract.name = f"Codex Gold Mask Hue Offset {name}"
    subtract.operation = "SUBTRACT"
    subtract.inputs[1].default_value = 0.10
    subtract.location = (-40, -260)

    absolute = tree.nodes.new("ShaderNodeMath")
    absolute.name = f"Codex Gold Mask Hue Distance {name}"
    absolute.operation = "ABSOLUTE"
    absolute.location = (130, -260)

    hue_mask = tree.nodes.new("ShaderNodeMath")
    hue_mask.name = f"Codex Gold Mask Hue Range {name}"
    hue_mask.operation = "LESS_THAN"
    hue_mask.inputs[1].default_value = 0.06
    hue_mask.location = (300, -260)

    saturation_mask = tree.nodes.new("ShaderNodeMath")
    saturation_mask.name = f"Codex Gold Mask Saturation {name}"
    saturation_mask.operation = "GREATER_THAN"
    saturation_mask.inputs[1].default_value = 0.08
    saturation_mask.location = (130, -360)

    value_mask = tree.nodes.new("ShaderNodeMath")
    value_mask.name = f"Codex Gold Mask Value {name}"
    value_mask.operation = "GREATER_THAN"
    value_mask.inputs[1].default_value = 0.32
    value_mask.location = (130, -460)

    multiply_hs = tree.nodes.new("ShaderNodeMath")
    multiply_hs.name = f"Codex Gold Mask Hue Saturation {name}"
    multiply_hs.operation = "MULTIPLY"
    multiply_hs.location = (480, -280)

    mask = tree.nodes.new("ShaderNodeMath")
    mask.name = f"Codex Gold Mask Final {name}"
    mask.operation = "MULTIPLY"
    mask.location = (650, -280)

    pbr = tree.nodes.new("ShaderNodeBsdfPrincipled")
    pbr.name = f"Codex Gold PBR {name}"
    pbr.label = f"Texture gold metal: {name}"
    pbr.location = (650, 80)
    set_input(pbr, "Metallic", 0.94)
    set_input(pbr, "Roughness", 0.16)
    set_input(pbr, "IOR", 1.45)
    set_input(pbr, "Specular IOR Level", 0.5)
    set_input(pbr, "Coat Weight", 0.08)
    set_input(pbr, "Coat Roughness", 0.12)

    mix = tree.nodes.new("ShaderNodeMixShader")
    mix.name = f"Codex Gold Mix {name}"
    mix.label = "Texture gold mask -> PBR metal"
    mix.location = (930, 60)

    tree.links.new(texture.outputs["Color"], separate.inputs["Color"])
    tree.links.new(separate.outputs[0], subtract.inputs[0])
    tree.links.new(subtract.outputs[0], absolute.inputs[0])
    tree.links.new(absolute.outputs[0], hue_mask.inputs[0])
    tree.links.new(separate.outputs[1], saturation_mask.inputs[0])
    tree.links.new(separate.outputs[2], value_mask.inputs[0])
    tree.links.new(hue_mask.outputs[0], multiply_hs.inputs[0])
    tree.links.new(saturation_mask.outputs[0], multiply_hs.inputs[1])
    tree.links.new(multiply_hs.outputs[0], mask.inputs[0])
    tree.links.new(value_mask.outputs[0], mask.inputs[1])
    tree.links.new(texture.outputs["Color"], pbr.inputs["Base Color"])
    tree.links.new(mask.outputs[0], mix.inputs[0])
    tree.links.new(shader.outputs["Shader"], mix.inputs[1])
    tree.links.new(pbr.outputs["BSDF"], mix.inputs[2])

    for link in list(tree.links):
        if link.to_node == output and link.to_socket.name == "Surface":
            tree.links.remove(link)
    tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])
    material["codex_gold_texture_mask"] = "hue_0.10_width_0.06_value_0.32"
    return True


def tint_metal_base_color(name, color, factor):
    material = bpy.data.materials.get(name)
    if not material or not material.node_tree:
        return False
    tree = material.node_tree
    texture = tree.nodes.get("mmd_base_tex")
    bsdf = tree.nodes.get(f"Codex Metal PBR {name}")
    if texture is None or bsdf is None:
        return False
    tint_name = f"Codex Metal Tint {name}"
    tint = tree.nodes.get(tint_name)
    if tint is None:
        tint = tree.nodes.new("ShaderNodeMixRGB")
        tint.name = tint_name
        tint.label = "Warm gold metal tint"
        tint.blend_type = "MIX"
        tint.location = (200, 120)
    tint.inputs[0].default_value = factor
    tint.inputs[2].default_value = (*color, 1.0)
    for link in list(tree.links):
        if link.to_node == bsdf and link.to_socket.name == "Base Color":
            tree.links.remove(link)
    tree.links.new(texture.outputs["Color"], tint.inputs[1])
    tree.links.new(tint.outputs["Color"], bsdf.inputs["Base Color"])
    material["codex_metal_tint"] = list(color)
    return True


def create_shoe_heel_material():
    shoe = bpy.data.materials.get("鞋子")
    obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
    if not shoe or not obj or not shoe.use_nodes or not shoe.node_tree:
        return 0
    texture = shoe.node_tree.nodes.get("mmd_base_tex")
    if not texture or not texture.image:
        return 0

    heel_name = "Codex Shoe Heel Metal"
    material = bpy.data.materials.get(heel_name)
    if material is None:
        material = bpy.data.materials.new(heel_name)
        material.use_nodes = True
        tree = material.node_tree
        tree.nodes.clear()
        output = tree.nodes.new("ShaderNodeOutputMaterial")
        texcoord = tree.nodes.new("ShaderNodeTexCoord")
        image = tree.nodes.new("ShaderNodeTexImage")
        image.image = texture.image
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.name = heel_name
        set_input(bsdf, "Metallic", 0.92)
        set_input(bsdf, "Roughness", 0.18)
        set_input(bsdf, "IOR", 1.45)
        set_input(bsdf, "Specular IOR Level", 0.5)
        set_input(bsdf, "Coat Weight", 0.10)
        set_input(bsdf, "Coat Roughness", 0.12)
        tree.links.new(texcoord.outputs["UV"], image.inputs["Vector"])
        tree.links.new(image.outputs["Color"], bsdf.inputs["Base Color"])
        tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
        material["codex_material_optimization"] = "v3_shoe_heel_pbr"
        material["codex_material_role"] = "metal"

    shoe_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material == shoe), None)
    if shoe_slot is None:
        return 0
    heel_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material == material), None)
    if heel_slot is None:
        obj.data.materials.append(material)
        heel_slot = len(obj.material_slots) - 1

    assigned = 0
    for poly in obj.data.polygons:
        if poly.material_index != shoe_slot:
            continue
        center = poly.center
        if center.y > 0.045 and center.z < 0.10:
            poly.material_index = heel_slot
            assigned += 1
    return assigned


def lift_ring_side_skin():
    source = bpy.data.materials.get("皮肤")
    obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
    if source is None or obj is None or not source.use_nodes or not source.node_tree:
        return 0

    name = "Codex Skin Right Leg Lift"
    material = bpy.data.materials.get(name)
    if material is None:
        material = source.copy()
        material.name = name
    balance = material.node_tree.nodes.get("Skin Color Balance")
    if balance is not None:
        set_input(balance, "Value", 1.08)
        set_input(balance, "Saturation", 1.01)
    material["codex_material_optimization"] = "v4_ring_side_skin_lift"
    material["codex_material_role"] = "skin"

    source_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material == source), None)
    if source_slot is None:
        return 0
    lift_slot = next((index for index, slot in enumerate(obj.material_slots) if slot.material == material), None)
    if lift_slot is None:
        obj.data.materials.append(material)
        lift_slot = len(obj.material_slots) - 1

    assigned = 0
    for poly in obj.data.polygons:
        if poly.material_index != source_slot:
            continue
        center = poly.center
        if center.x < -0.02 and 0.45 < center.z < 0.90:
            poly.material_index = lift_slot
            assigned += 1
    return assigned


metal_materials = {
    "头饰金属": 0.14,
    "耳坠": 0.16,
    "项链金属": 0.17,
    "metal leg": 0.18,
}
changed_materials = [name for name, roughness in metal_materials.items() if rebuild_metal_material(name, roughness)]
tint_metal_base_color("metal leg", (0.95, 0.56, 0.12), 0.40)
gold_mask_materials = {
    "头饰", "袖子", "袖子2", "鞋子", "外裙子", "外裙子2", "外裙子前外",
    "外裙子内侧", "外裙子内里", "外裙子隐藏", "前带子", "后带子", "前带子两条",
}
masked_materials = [name for name in sorted(gold_mask_materials) if apply_gold_texture_mask(name)]
shoe_heel_faces = create_shoe_heel_material()


def configure_area(name, location, energy, color, size, target, shape="DISK", size_y=None):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "LIGHT":
        data = bpy.data.lights.new(name=f"{name}_Data", type="AREA")
        obj = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(obj)
    data = obj.data
    data.type = "AREA"
    data.energy = energy
    data.color = color
    data.shape = shape
    data.size = size
    if shape == "RECTANGLE" and size_y is not None:
        data.size_y = size_y
    obj.location = location
    point_at(obj, target)
    obj["codex_lighting_rig"] = "v2_broad_fill_metal"
    return obj


configure_area("Key_Soft", (-2.4, -3.2, 3.6), 270.0, (1.0, 0.78, 0.64), 3.2, CHARACTER_TARGET)
configure_area("Rim_Cool", (2.4, 1.4, 3.2), 300.0, (0.42, 0.62, 1.0), 3.0, CHARACTER_TARGET)
configure_area("Fill_Front", (2.8, -3.4, 1.8), 95.0, (0.62, 0.76, 1.0), 3.8, CHARACTER_TARGET)
configure_area("Skin_Fill", (-1.8, -2.6, 1.65), 80.0, (1.0, 0.58, 0.46), 2.6, FACE_TARGET)
configure_area("EyeLight", (0.0, -2.6, 1.8), 40.0, (1.0, 0.82, 0.72), 1.2, FACE_TARGET)
configure_area("Overhead_Soft", (0.0, 0.0, 4.0), 80.0, (1.0, 0.92, 0.86), 2.8, CHARACTER_TARGET)
configure_area("Side_Fill_Left", (-3.2, 0.0, 1.8), 75.0, (0.50, 0.66, 1.0), 3.0, CHARACTER_TARGET)
configure_area("Back_Fill_Warm", (0.0, 3.2, 1.8), 115.0, (1.0, 0.42, 0.28), 2.8, CHARACTER_TARGET)
configure_area("Metal_Strip_Key", (-1.25, -2.0, 2.55), 160.0, (1.0, 0.78, 0.56), 0.32, FACE_TARGET, "RECTANGLE", 1.8)
configure_area("Metal_Strip_Rim", (1.35, 1.1, 2.7), 190.0, (0.50, 0.70, 1.0), 0.38, FACE_TARGET, "RECTANGLE", 2.0)
configure_area("Leg_Fill_Front", (0.0, -3.0, 0.72), 120.0, (1.0, 0.76, 0.66), 2.4, Vector((0.02, 0.18, 0.70)))
configure_area("Leg_Fill_Right", (2.0, -1.7, 0.72), 70.0, (0.60, 0.72, 1.0), 2.2, Vector((0.02, 0.18, 0.70)))
left_fill = configure_area("Leg_Fill_Left", (-2.0, -1.8, 0.78), 115.0, (1.0, 0.72, 0.60), 2.2, Vector((-0.08, 0.18, 0.70)))
left_fill.data.use_shadow = False
ring_fill = configure_area("Leg_Fill_Ring", (-0.85, -1.75, 0.72), 75.0, (1.0, 0.76, 0.66), 1.25, Vector((-0.077, 0.02, 0.72)))
ring_fill.data.use_shadow = False

warm_point = bpy.data.objects.get("Practical_Warm")
if warm_point and warm_point.type == "LIGHT":
        warm_point.data.energy = 32.0

for lantern_name in ("Lantern_A", "Lantern_B", "Lantern_C"):
    lantern = bpy.data.objects.get(lantern_name)
    if lantern:
        lantern.hide_render = True

scene = bpy.context.scene
if scene.world:
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.025, 0.040, 0.075, 1.0)
        background.inputs["Strength"].default_value = 0.07
if scene.render.engine == "CYCLES":
    scene.cycles.glossy_bounces = max(scene.cycles.glossy_bounces, 6)
scene.view_settings.exposure = -0.30

print("PBR metal materials: " + ", ".join(changed_materials))
print("Gold texture mask materials: " + ", ".join(masked_materials))
print("Shoe heel metal faces: " + str(shoe_heel_faces))
print("Lighting rig configured: v2_broad_fill_metal")
