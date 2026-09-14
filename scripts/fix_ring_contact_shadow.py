import bpy

mat = bpy.data.materials.get("metal leg")
if mat is None or not mat.use_nodes or not mat.node_tree:
    raise RuntimeError("metal leg material not found")
tree = mat.node_tree
pbr = tree.nodes.get("Codex Metal PBR metal leg")
output = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
if pbr is None or output is None:
    raise RuntimeError("metal leg shader nodes not found")

for n in list(tree.nodes):
    if n.name.startswith("Codex Ring Shadow"):
        tree.nodes.remove(n)

lightpath = tree.nodes.new("ShaderNodeLightPath")
lightpath.name = "Codex Ring Shadow LightPath"
lightpath.location = (640, -120)

transparent = tree.nodes.new("ShaderNodeBsdfTransparent")
transparent.name = "Codex Ring Shadow Transparent"
transparent.location = (640, 120)

mix = tree.nodes.new("ShaderNodeMixShader")
mix.name = "Codex Ring Shadow Mix"
mix.label = "Ring visible but casts no shadow"
mix.location = (880, 60)

tree.links.new(pbr.outputs["BSDF"], mix.inputs[1])
tree.links.new(transparent.outputs["BSDF"], mix.inputs[2])
tree.links.new(lightpath.outputs["Is Shadow Ray"], mix.inputs[0])

for link in list(tree.links):
    if link.to_node == output and link.to_socket.name == "Surface":
        tree.links.remove(link)
tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])

mat["codex_ring_shadow"] = "no_cast_via_lightpath"
print("metal leg ring no longer casts shadows")
