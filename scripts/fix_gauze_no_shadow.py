import bpy

# Sheer gauze panels hang between key light and thighs; as solid shadow
# casters they stripe the legs. Make them invisible to shadow rays only.
TARGETS = ("前带子两条",)

for mat_name in TARGETS:
    mat = bpy.data.materials.get(mat_name)
    if mat is None or not mat.use_nodes or not mat.node_tree:
        print(f"skip {mat_name}: not found")
        continue
    tree = mat.node_tree
    output = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if output is None:
        print(f"skip {mat_name}: no output")
        continue
    for n in list(tree.nodes):
        if n.name.startswith("Codex NoCast"):
            tree.nodes.remove(n)

    surf_link = next((l for l in tree.links
                      if l.to_node == output and l.to_socket.name == "Surface"), None)
    if surf_link is None:
        print(f"skip {mat_name}: surface not linked")
        continue
    src_node, src_socket = surf_link.from_node, surf_link.from_socket.name

    lightpath = tree.nodes.new("ShaderNodeLightPath")
    lightpath.name = "Codex NoCast LightPath"
    lightpath.location = (820, -160)

    transparent = tree.nodes.new("ShaderNodeBsdfTransparent")
    transparent.name = "Codex NoCast Transparent"
    transparent.location = (820, 120)

    mix = tree.nodes.new("ShaderNodeMixShader")
    mix.name = "Codex NoCast Mix"
    mix.label = "Sheer fabric casts no shadow"
    mix.location = (1060, 60)

    tree.links.new(src_node.outputs[src_socket], mix.inputs[1])
    tree.links.new(transparent.outputs["BSDF"], mix.inputs[2])
    tree.links.new(lightpath.outputs["Is Shadow Ray"], mix.inputs[0])
    tree.links.remove(surf_link)
    tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])
    mat["codex_nocast_shadow"] = "sheer_gauze"
    print(f"nocast applied: {mat_name}")
