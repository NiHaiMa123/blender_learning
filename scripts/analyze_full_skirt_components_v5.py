import bpy
import bmesh
import json
from collections import Counter, defaultdict, deque

SOURCE = '鸣潮_今汐_桃夭灼灼1.0311_mesh'
PATH = r'D:\software\blender\project\今汐_夜晚湖畔.blend'
MATERIALS = {
    '外裙子', '外裙子前外', '外裙子内里', '外裙子2', '外裙子隐藏',
    '外裙子内侧', '前带子', '后带子', '前带子两条', '纱内侧', '纱外侧',
}

bpy.ops.wm.open_mainfile(filepath=PATH)
scene = bpy.context.scene
scene.frame_set(100)
bpy.context.view_layer.update()
source = bpy.data.objects[SOURCE]
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = source.evaluated_get(depsgraph)
evaluated_mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
material_names = [material.name if material else '' for material in evaluated_mesh.materials]
candidate_ids = {index for index, name in enumerate(material_names) if name in MATERIALS}

bm = bmesh.new()
bm.from_mesh(evaluated_mesh)
remove = [face for face in bm.faces if face.material_index not in candidate_ids]
bmesh.ops.delete(bm, geom=remove, context='FACES')
loose = [vertex for vertex in bm.verts if not vertex.link_faces]
if loose:
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

adjacency = defaultdict(set)
for edge in bm.edges:
    if not edge.link_faces:
        continue
    a, b = edge.verts[0].index, edge.verts[1].index
    adjacency[a].add(b)
    adjacency[b].add(a)
seen = set()
components = []
for start in range(len(bm.verts)):
    if start in seen:
        continue
    queue = deque([start])
    seen.add(start)
    vertices = []
    while queue:
        vertex = queue.popleft()
        vertices.append(vertex)
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    vertex_set = set(vertices)
    faces = [
        face for face in bm.faces
        if any(vertex.index in vertex_set for vertex in face.verts)
    ]
    zs = [float(bm.verts[index].co.z) for index in vertices]
    xs = [float(bm.verts[index].co.x) for index in vertices]
    ys = [float(bm.verts[index].co.y) for index in vertices]
    materials = Counter(material_names[face.material_index] for face in faces)
    components.append({
        'vertices': len(vertices),
        'faces': len(faces),
        'z_min': min(zs),
        'z_max': max(zs),
        'z_span': max(zs) - min(zs),
        'x_min': min(xs),
        'x_max': max(xs),
        'x_center': sum(xs) / len(xs),
        'y_min': min(ys),
        'y_max': max(ys),
        'y_center': sum(ys) / len(ys),
        'materials': dict(materials),
    })

components.sort(key=lambda item: item['vertices'], reverse=True)
report = {
    'candidate_materials': sorted(MATERIALS),
    'candidate_vertices': len(bm.verts),
    'candidate_faces': len(bm.faces),
    'components': len(components),
    'component_stats': components,
}
with open(
    r'D:\project\blender_learning\validation\full_skirt_components_v5.json',
    'w',
    encoding='utf-8',
) as handle:
    json.dump(report, handle, ensure_ascii=False, indent=2)
print('FULL_SKIRT_COMPONENTS|' + json.dumps(report, ensure_ascii=False))
bm.free()
evaluated.to_mesh_clear()
