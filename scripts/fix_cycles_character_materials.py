import bpy

obj = bpy.data.objects.get("卡提希娅_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")


def input_by_name(node, *names):
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            return socket
    return None


def rebuild_principled(mat, kind, overlay_alpha=None):
    tree = mat.node_tree
    tex = tree.nodes.get("mmd_base_tex")
    if tex is None or tex.type != 'TEX_IMAGE':
        raise RuntimeError(f"{mat.name}: base texture node missing")

    # Remove only the replacement nodes from previous runs, keeping the
    # original MMD graph intact so the change remains easy to reverse.
    for node in list(tree.nodes):
        if node.name.startswith("Codex Cycles"):
            tree.nodes.remove(node)

    out = next((n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if out is None:
        out = tree.nodes.new('ShaderNodeOutputMaterial')

    bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.name = f"Codex Cycles {kind}"
    bsdf.label = f"Cycles-safe {kind}"
    bsdf.location = (420, 40)

    tree.links.new(tex.outputs['Color'], input_by_name(bsdf, 'Base Color'))
    input_by_name(bsdf, 'Metallic').default_value = 0.0
    input_by_name(bsdf, 'Roughness').default_value = 0.42 if kind == 'Hair' else 0.50
    ior_level = input_by_name(bsdf, 'IOR Level', 'Specular IOR Level')
    if ior_level:
        ior_level.default_value = 0.28 if kind == 'Hair' else 0.22

    if kind == 'Skin':
        subsurface = input_by_name(bsdf, 'Subsurface Weight', 'Subsurface')
        if subsurface:
            subsurface.default_value = 0.035
        radius = input_by_name(bsdf, 'Subsurface Radius')
        if radius:
            radius.default_value = (1.0, 0.45, 0.3)

    alpha = input_by_name(bsdf, 'Alpha')
    if overlay_alpha is None:
        # Skin and the structural hair shells are genuinely opaque.  The MMD
        # node group multiplies texture/toon alpha and can punch them away in
        # Cycles even though Eevee displays them as intended.
        alpha.default_value = 1.0
        mat.surface_render_method = 'DITHERED'
    else:
        mul = tree.nodes.new('ShaderNodeMath')
        mul.name = "Codex Cycles Overlay Alpha"
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = overlay_alpha
        mul.location = (190, -220)
        tree.links.new(tex.outputs['Alpha'], mul.inputs[0])
        tree.links.new(mul.outputs[0], alpha)
        mat.surface_render_method = 'DITHERED'

    for link in list(out.inputs['Surface'].links):
        tree.links.remove(link)
    tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat.use_backface_culling = False


material_kinds = {
    'Face_': ('Skin', None),
    'Up_Skin': ('Skin', None),
    'Hair_Bangs': ('Hair', None),
    'Hair_Back': ('Hair', None),
    'Hair_Bangs+': ('Hair', 0.38),
    'Hair_Back+': ('Hair', 0.38),
}

fixed = []
for slot in obj.material_slots:
    mat = slot.material
    if mat and mat.name in material_kinds:
        rebuild_principled(mat, *material_kinds[mat.name])
        fixed.append(mat.name)

# Allow the layered hair highlights to pass without exhausting Cycles'
# transparent path budget.
scene = bpy.data.scenes.get('Codex_Cycles_Render')
if scene and hasattr(scene.cycles, 'transparent_max_bounces'):
    scene.cycles.transparent_max_bounces = max(scene.cycles.transparent_max_bounces, 16)

print("Fixed Cycles materials: " + ", ".join(fixed))
return_value = fixed
