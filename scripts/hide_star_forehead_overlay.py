import bpy, json

mat = bpy.data.materials['Star']
mat.use_nodes = True
tree = mat.node_tree
for node in list(tree.nodes):
    if node.name.startswith('Codex Hide Forehead'):
        tree.nodes.remove(node)
out = next((n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL'), None)
if out is None:
    out = tree.nodes.new('ShaderNodeOutputMaterial')
transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
transparent.name = 'Codex Hide Forehead Star Overlay'
transparent.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
for link in list(out.inputs['Surface'].links):
    tree.links.remove(link)
tree.links.new(transparent.outputs['BSDF'], out.inputs['Surface'])
mat.surface_render_method = 'DITHERED'
mat.use_backface_culling = False
if hasattr(mat, 'use_transparency_overlap'):
    mat.use_transparency_overlap = False

for area in bpy.context.window.screen.areas:
    area.tag_redraw()

path = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)
result = {'material': mat.name, 'mode': 'fully_transparent', 'saved': path}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
