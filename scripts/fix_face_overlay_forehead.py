import bpy, json

obj = bpy.data.objects['卡提希娅_mesh']
mat = bpy.data.materials.get('Face+')
if mat is None or not mat.use_nodes:
    raise RuntimeError('Face+ overlay material not found')

tree = mat.node_tree
tex = tree.nodes.get('mmd_base_tex')
if tex is None or tex.type != 'TEX_IMAGE':
    raise RuntimeError('Face+ base texture node not found')

for node in list(tree.nodes):
    if node.name.startswith('Codex Face Overlay'):
        tree.nodes.remove(node)

out = next((n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL'), None)
if out is None:
    out = tree.nodes.new('ShaderNodeOutputMaterial')

bsdf = tree.nodes.new('ShaderNodeBsdfPrincipled')
bsdf.name = 'Codex Face Overlay Principled'
bsdf.location = (420, 20)
bsdf.inputs['Roughness'].default_value = 0.52
if bsdf.inputs.get('IOR Level'):
    bsdf.inputs['IOR Level'].default_value = 0.18

tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
tree.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
for link in list(out.inputs['Surface'].links):
    tree.links.remove(link)
tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

mat.surface_render_method = 'DITHERED'
mat.use_backface_culling = False
if hasattr(mat, 'use_transparency_overlap'):
    mat.use_transparency_overlap = False

for area in bpy.context.window.screen.areas:
    area.tag_redraw()

path = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)

result = {
    'material': mat.name,
    'texture': tex.image.name if tex.image else None,
    'alpha_linked': bsdf.inputs['Alpha'].is_linked,
    'surface_render_method': mat.surface_render_method,
    'saved': path,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
