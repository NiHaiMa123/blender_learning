import bpy
import json
import os


def set_socket(node, names, value):
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None and not socket.is_linked:
            socket.default_value = value
            return True
    return False


def tune_mmd_material(name, specular_color, reflect, glossy_mix, role):
    material = bpy.data.materials.get(name)
    if not material or not material.use_nodes or not material.node_tree:
        return None
    shader = material.node_tree.nodes.get("mmd_shader")
    if not shader:
        return None

    # Keep the imported MMD group untouched and give each tuned material its
    # own controlled diffuse/glossy balance.
    if shader.node_tree and shader.node_tree.name == "MMDShaderDev":
        group = shader.node_tree.copy()
        group.name = f"Codex_{name}_MMDShader"
        shader.node_tree = group
    group = shader.node_tree
    mix = group.nodes.get("混合着色器") if group else None
    if mix is None and group:
        mix = next((node for node in group.nodes if node.type == "MIX_SHADER"), None)
    if mix is not None:
        set_socket(mix, ("Fac",), glossy_mix)

    if "codex_material_optimization" not in material:
        material["codex_material_optimization"] = "v1_skin_sheen_metal"
        material["codex_material_role"] = role

    set_socket(shader, ("Specular Color",), specular_color)
    set_socket(shader, ("Reflect",), reflect)
    return {"material": name, "role": role, "reflect": reflect}


def tune_skin_material(name, weight, roughness):
    material = bpy.data.materials.get(name)
    if not material or not material.use_nodes or not material.node_tree:
        return None
    node = material.node_tree.nodes.get("Skin Principled")
    if node is None:
        node = next((item for item in material.node_tree.nodes if item.type == "BSDF_PRINCIPLED"), None)
    if node is None:
        return None

    if "codex_material_optimization" not in material:
        material["codex_material_optimization"] = "v1_skin_sheen_metal"
        material["codex_material_role"] = "skin"

    set_socket(node, ("Subsurface Weight", "Subsurface"), weight)
    set_socket(node, ("Subsurface Radius",), (1.0, 0.46, 0.30))
    set_socket(node, ("Subsurface Scale",), 0.045)
    set_socket(node, ("Roughness",), roughness)
    set_socket(node, ("IOR",), 1.4)
    set_socket(node, ("Specular IOR Level", "IOR Level"), 0.32)
    return {"material": name, "role": "skin", "subsurface": weight, "roughness": roughness}


metal_names = {"头饰金属", "耳坠", "项链金属", "项链花", "metal leg"}
fabric_names = {
    "头饰", "白", "外裙子", "外裙子2", "外裙子内侧", "外裙子内里", "外裙子前外",
    "外裙子隐藏", "袖子", "袖子2", "纱内侧", "纱外侧", "鞋子", "前带子",
    "前带子两条", "后带子",
}

changes = []
for name in sorted(metal_names):
    result = tune_mmd_material(name, (0.98, 0.68, 0.28, 1.0), 0.10, 0.46, "metal")
    if result:
        changes.append(result)

for name in sorted(fabric_names):
    result = tune_mmd_material(name, (0.66, 0.62, 0.80, 1.0), 0.18, 0.20, "fabric_sheen")
    if result:
        changes.append(result)

for name, weight, roughness in (("皮肤", 0.34, 0.34), ("face", 0.26, 0.32)):
    result = tune_skin_material(name, weight, roughness)
    if result:
        changes.append(result)

for scene in bpy.data.scenes:
    if scene.render.engine == "CYCLES":
        scene.cycles.glossy_bounces = max(scene.cycles.glossy_bounces, 6)

output = r"D:\project\blender_learning\renders\今汐_material_optimized.blend"
os.makedirs(os.path.dirname(output), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output, copy=True, check_existing=False)

print(json.dumps({"changes": changes, "blend": output}, ensure_ascii=False, indent=2))
