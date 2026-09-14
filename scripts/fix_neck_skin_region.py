import bpy

obj = bpy.data.objects['卡提希娅_mesh']

source_index = next(
    i for i, slot in enumerate(obj.material_slots)
    if slot.material and slot.material.name == 'Up_Skin'
)

neck_mat = bpy.data.materials.get('Codex_Neck_Skin')
if neck_mat is None:
    neck_mat = bpy.data.materials.new('Codex_Neck_Skin')
    neck_mat.use_nodes = True
nt = neck_mat.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
skin_color = (0.95, 0.50, 0.46, 1.0)
bsdf.inputs['Base Color'].default_value = skin_color
bsdf.inputs['Roughness'].default_value = 0.50
if bsdf.inputs.get('IOR Level'):
    bsdf.inputs['IOR Level'].default_value = 0.22
if bsdf.inputs.get('Subsurface Weight'):
    bsdf.inputs['Subsurface Weight'].default_value = 0.035
if bsdf.inputs.get('Emission Color'):
    # A small stylized fill prevents the deeply occluded area under the chin
    # from reading as a literal hole at full-body scale.
    bsdf.inputs['Emission Color'].default_value = (0.30, 0.10, 0.085, 1.0)
if bsdf.inputs.get('Emission Strength'):
    bsdf.inputs['Emission Strength'].default_value = 0.22
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
neck_mat.use_backface_culling = False
neck_mat.surface_render_method = 'DITHERED'

neck_index = None
for i, slot in enumerate(obj.material_slots):
    if slot.material == neck_mat:
        neck_index = i
        break
if neck_index is None:
    obj.data.materials.append(neck_mat)
    neck_index = len(obj.material_slots) - 1

group_indices = []
for name in ('首', '頭'):
    group = obj.vertex_groups.get(name)
    if group:
        group_indices.append(group.index)

def neck_weight(vertex):
    return sum(g.weight for g in vertex.groups if g.group in group_indices)

changed = 0
for poly in obj.data.polygons:
    if poly.material_index not in (source_index, neck_index):
        continue
    center_z = sum(obj.data.vertices[i].co.z for i in poly.vertices) / len(poly.vertices)
    max_weight = max(neck_weight(obj.data.vertices[i]) for i in poly.vertices)
    # This isolates the actual neck tube.  Shoulder/chest polygons are below
    # this rest-space height and remain on the textured body material.
    if center_z >= 1.375 and max_weight >= 0.10:
        if poly.material_index != neck_index:
            poly.material_index = neck_index
            changed += 1

print(f'Neck skin slot {neck_index}; reassigned {changed} polygons')
return_value = {'slot': neck_index, 'polygons': changed}
