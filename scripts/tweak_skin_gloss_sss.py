import bpy

# Skin gloss + translucency pass (idempotent, absolute values):
# - broader/softer specular sheen, clearcoat moisture layer
# - stronger subsurface for fleshy translucency
TARGETS = {
    "Roughness": 0.24,
    "Specular IOR Level": 0.5,
    "Coat Weight": 0.22,
    "Coat Roughness": 0.18,
    "Subsurface Weight": 0.6,
    "Subsurface Scale": 0.06,
}
RADIUS = (1.2, 0.5, 0.35)

mat = bpy.data.materials.get("皮肤")
if mat is None or not mat.use_nodes or not mat.node_tree:
    raise RuntimeError("Skin material not found")
shader = mat.node_tree.nodes.get("Skin Principled")
if shader is None:
    raise RuntimeError("Skin Principled not found")

applied = {}
for name, value in TARGETS.items():
    sock = shader.inputs.get(name)
    if sock is None:
        raise RuntimeError(f"Principled input missing: {name}")
    sock.default_value = value
    applied[name] = value

radius_sock = shader.inputs.get("Subsurface Radius")
if radius_sock is not None:
    radius_sock.default_value = RADIUS
    applied["Subsurface Radius"] = list(RADIUS)

mat["codex_skin_gloss_sss"] = "r0.24_spec0.5_coat0.22_sss0.6_rad120"
print(f"skin gloss/sss updated: {applied}")
