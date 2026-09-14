import bpy
import bmesh
import json
import os
from collections import defaultdict, deque
from mathutils import Matrix

SOURCE_NAME = '鸣潮_今汐_桃夭灼灼1.0311_mesh'
POSE_BACKUP_PATH = r'D:\software\blender\project\今汐_before_cloth_rebuild_posed_source.blend'
OUTPUT_PATH = r'D:\software\blender\project\今汐_cloth_rebuild_pose_v8.blend'
MANIFEST_DIR = r'D:\project\blender_learning\cache\cloth_rebuild_pose_v8'

SKIRT_MATERIALS = {
    '外裙子', '外裙子前外', '外裙子内里', '外裙子2', '外裙子隐藏',
    '外裙子内侧', '前带子', '后带子', '前带子两条', '纱内侧', '纱外侧',
}
COLLIDER_MATERIALS = {'皮肤'}

scene = bpy.context.scene
source_frame = scene.frame_current
source = bpy.data.objects.get(SOURCE_NAME)
if source is None or source.type != 'MESH':
    raise RuntimeError('Source mesh not found: ' + SOURCE_NAME)

armature_modifier = next(
    (modifier for modifier in source.modifiers if modifier.type == 'ARMATURE'),
    None,
)
armature = armature_modifier.object if armature_modifier else None
if armature is None:
    raise RuntimeError('The source mesh has no armature modifier')

identity = Matrix.Identity(4)
posed_bones = []
for bone in armature.pose.bones:
    delta = max(
        abs(bone.matrix_basis[row][col] - identity[row][col])
        for row in range(4) for col in range(4)
    )
    if delta > 1e-5:
        posed_bones.append(bone.name)

# Capture the exact user-authored pose before creating any derived objects.
scene.frame_set(source_frame)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(
    filepath=POSE_BACKUP_PATH,
    copy=True,
    check_existing=False,
)

for obj in list(bpy.data.objects):
    if obj.name.startswith('CLOTH_REBUILD_'):
        bpy.data.objects.remove(obj, do_unlink=True)
for collection in list(bpy.data.collections):
    if collection.name.startswith('CLOTH_REBUILD'):
        bpy.data.collections.remove(collection)

root = bpy.data.collections.new('CLOTH_REBUILD')
scene.collection.children.link(root)
support = bpy.data.collections.new('CLOTH_REBUILD_SUPPORT')
scene.collection.children.link(support)

depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = source.evaluated_get(depsgraph)
evaluated_mesh = evaluated.to_mesh(
    preserve_all_data_layers=True,
    depsgraph=depsgraph,
)

material_names = [material.name if material else '' for material in evaluated_mesh.materials]
skirt_ids = {index for index, name in enumerate(material_names) if name in SKIRT_MATERIALS}
collider_ids = {index for index, name in enumerate(material_names) if name in COLLIDER_MATERIALS}
if not skirt_ids:
    evaluated.to_mesh_clear()
    raise RuntimeError('No skirt material slots found')
if not collider_ids:
    evaluated.to_mesh_clear()
    raise RuntimeError('No skin material slot found for collision')

# Material slots are reused by the bodice and waist decorations. Select only
# connected garment components that extend far enough below the waist to be cloth.
candidate_faces = {
    polygon.index for polygon in evaluated_mesh.polygons
    if polygon.material_index in skirt_ids
}
vertex_to_faces = defaultdict(set)
for face_index in candidate_faces:
    for vertex_index in evaluated_mesh.polygons[face_index].vertices:
        vertex_to_faces[vertex_index].add(face_index)
face_adjacency = defaultdict(set)
for linked_faces in vertex_to_faces.values():
    for face_index in linked_faces:
        face_adjacency[face_index].update(linked_faces - {face_index})
seen_faces = set()
source_components = []
for start in candidate_faces:
    if start in seen_faces:
        continue
    queue = deque([start])
    seen_faces.add(start)
    faces = []
    while queue:
        face_index = queue.popleft()
        faces.append(face_index)
        for neighbor in face_adjacency[face_index]:
            if neighbor not in seen_faces:
                seen_faces.add(neighbor)
                queue.append(neighbor)
    vertices = {
        vertex_index
        for face_index in faces
        for vertex_index in evaluated_mesh.polygons[face_index].vertices
    }
    zs = [float(evaluated_mesh.vertices[index].co.z) for index in vertices]
    ys = [float(evaluated_mesh.vertices[index].co.y) for index in vertices]
    source_components.append({
        'faces': faces,
        'vertices': vertices,
        'z_min': min(zs),
        'z_max': max(zs),
        'y_center': sum(ys) / len(ys),
        'materials': {
            material_names[evaluated_mesh.polygons[face_index].material_index]
            for face_index in faces
        },
    })

dynamic_components = [
    component for component in source_components
    if component['materials'].issubset({'纱内侧', '纱外侧'})
    and component['y_center'] > 0.1
    and component['z_min'] < 0.9
    and component['z_max'] - component['z_min'] > 0.18
    and len(component['vertices']) >= 300
    and len(component['faces']) >= 400
]
dynamic_face_ids = {
    face_index
    for component in dynamic_components
    for face_index in component['faces']
}
if not dynamic_face_ids:
    evaluated.to_mesh_clear()
    raise RuntimeError('Component filter selected no lower-skirt faces')


def filtered_mesh(name, keep_face):
    mesh = evaluated_mesh.copy()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    remove = [face for face in bm.faces if not keep_face(face)]
    if remove:
        bmesh.ops.delete(bm, geom=remove, context='FACES')
    loose = [vertex for vertex in bm.verts if not vertex.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(mesh)
    bm.free()
    mesh.name = name
    mesh.update(calc_edges=True)
    return mesh


def make_object(name, mesh, collection):
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.matrix_world = source.matrix_world.copy()
    return obj


body_mesh = filtered_mesh(
    'CLOTH_REBUILD_BODY_STATIC_MESH',
    lambda face: face.index not in dynamic_face_ids,
)
cloth_mesh = filtered_mesh(
    'CLOTH_REBUILD_SKIRT_MESH',
    lambda face: face.index in dynamic_face_ids,
)
collider_mesh = filtered_mesh(
    'CLOTH_REBUILD_COLLIDER_MESH',
    lambda face: face.material_index in collider_ids,
)

body = make_object('CLOTH_REBUILD_BODY_STATIC', body_mesh, root)
cloth_obj = make_object('CLOTH_REBUILD_SKIRT', cloth_mesh, root)
collider = make_object('CLOTH_REBUILD_BODY_COLLIDER', collider_mesh, support)
evaluated.to_mesh_clear()

body['role'] = 'visible posed character with only simulated skirt faces removed'
cloth_obj['role'] = 'posed skirt simulated by Blender Cloth'
cloth_obj['source_frame'] = source_frame
collider['role'] = 'posed skin collision surface; intentionally non-rendering'

# The complete rig and authored pose remain in the file as the editable source.
source['cloth_rebuild_original_hide_viewport'] = bool(source.hide_viewport)
source['cloth_rebuild_original_hide_render'] = bool(source.hide_render)
source.hide_viewport = True
source.hide_render = True
collider.display_type = 'WIRE'
collider.show_in_front = False
collider.hide_render = True

adjacency = defaultdict(set)
for edge in cloth_mesh.edges:
    a, b = edge.vertices
    adjacency[a].add(b)
    adjacency[b].add(a)
seen = set()
components = []
for start in range(len(cloth_mesh.vertices)):
    if start in seen:
        continue
    queue = deque([start])
    seen.add(start)
    component = []
    while queue:
        vertex = queue.popleft()
        component.append(vertex)
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    components.append(component)

pin_ids = set()
for component in components:
    top = max(cloth_mesh.vertices[index].co.z for index in component)
    pin_ids.update(
        index for index in component
        if cloth_mesh.vertices[index].co.z >= top - 0.05
    )
pin = cloth_obj.vertex_groups.new(name='CLOTH_PIN_WAIST')
pin.add(sorted(pin_ids), 1.0, 'REPLACE')

cloth = cloth_obj.modifiers.new('CLOTH_REBUILD_SKIRT', 'CLOTH')
settings = cloth.settings
settings.quality = 7
settings.mass = 0.25
settings.air_damping = 15.0
settings.tension_stiffness = 120.0
settings.compression_stiffness = 120.0
settings.shear_stiffness = 70.0
settings.bending_stiffness = 4.0
settings.tension_damping = 30.0
settings.compression_damping = 30.0
settings.shear_damping = 30.0
settings.bending_damping = 12.0
settings.pin_stiffness = 1.0
settings.time_scale = 0.5
settings.vertex_group_mass = pin.name
settings.effector_weights.gravity = 1.0

cloth_collision = cloth.collision_settings
cloth_collision.use_collision = True
cloth_collision.use_self_collision = False
cloth_collision.collision_quality = 5
cloth_collision.distance_min = 0.002
cloth_collision.damping = 0.5
cloth_collision.friction = 0.2

# The source skin is already a valid collision surface. Solidifying it creates a
# double shell around garment intersections and ejects the rear panels sideways.
collider.modifiers.new('CLOTH_REBUILD_COLLISION', 'COLLISION')
body_collision = collider.collision
body_collision.use = True
body_collision.use_culling = False
body_collision.use_normal = False
body_collision.thickness_outer = 0.004
body_collision.thickness_inner = 0.002
body_collision.damping = 0.35
body_collision.cloth_friction = 1.0

cache = cloth.point_cache
cache.frame_start = 1
cache.frame_end = 120
cache.frame_step = 1
cache.use_disk_cache = True
scene.frame_start = 1
scene.frame_end = 120
scene.frame_set(1)

os.makedirs(MANIFEST_DIR, exist_ok=True)
manifest = {
    'source_blend': bpy.data.filepath,
    'source_object': SOURCE_NAME,
    'source_frame': source_frame,
    'pose_backup': POSE_BACKUP_PATH,
    'output': OUTPUT_PATH,
    'root_location': [float(value) for value in source.parent.parent.location],
    'root_rotation': [float(value) for value in source.parent.parent.rotation_euler],
    'posed_bones': len(posed_bones),
    'mesh': {
        'source_vertices': len(source.data.vertices),
        'body_vertices': len(body_mesh.vertices),
        'body_faces': len(body_mesh.polygons),
        'cloth_vertices': len(cloth_mesh.vertices),
        'cloth_faces': len(cloth_mesh.polygons),
        'collider_vertices': len(collider_mesh.vertices),
        'collider_faces': len(collider_mesh.polygons),
        'components': len(components),
        'source_candidate_components': len(source_components),
        'dynamic_source_components': len(dynamic_components),
    },
    'pin_vertices': len(pin_ids),
    'free_vertices': len(cloth_mesh.vertices) - len(pin_ids),
    'pin_weight': 1.0,
}
with open(
    os.path.join(MANIFEST_DIR, 'build_manifest.json'),
    'w',
    encoding='utf-8',
) as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)

bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH, check_existing=False)
print('POSE_REBUILD|' + json.dumps(manifest, ensure_ascii=False))
