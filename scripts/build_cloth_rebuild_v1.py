import bpy
import bmesh
import json
import os
from mathutils import Vector

SOURCE_NAME = '鸣潮_今汐_桃夭灼灼1.0311_mesh'
SOURCE_FRAME = 100
BACKUP_PATH = r'D:\software\blender\project\今汐_before_cloth_rebuild.blend'
OUTPUT_PATH = r'D:\software\blender\project\今汐_cloth_rebuild_v3.blend'
CACHE_DIR = r'D:\project\blender_learning\cache\cloth_rebuild_v3'
PREVIEW_END = 80

SKIRT_MATERIALS = {'外裙子', '外裙子前外', '外裙子2', '外裙子隐藏'}
COLLIDER_MATERIALS = {'皮肤'}

source = bpy.data.objects.get(SOURCE_NAME)
if source is None or source.type != 'MESH':
    raise RuntimeError('Source mesh not found: ' + SOURCE_NAME)

# Preserve the original scene before replacing the visible mesh with the static split.
# Keep the first backup immutable so reruns never overwrite the source safety copy.
if not os.path.exists(BACKUP_PATH):
    bpy.ops.wm.save_as_mainfile(filepath=BACKUP_PATH, copy=True, check_existing=False)

# Remove only artifacts from a previous rebuild attempt.
for obj in list(bpy.data.objects):
    if obj.name.startswith('CLOTH_REBUILD_'):
        bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    if col.name.startswith('CLOTH_REBUILD_'):
        bpy.data.collections.remove(col)

root = bpy.data.collections.new('CLOTH_REBUILD')
bpy.context.scene.collection.children.link(root)
b_support = bpy.data.collections.new('CLOTH_REBUILD_SUPPORT')
bpy.context.scene.collection.children.link(b_support)

scene = bpy.context.scene
scene.frame_set(SOURCE_FRAME)
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated = source.evaluated_get(depsgraph)
evaluated_mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

material_names = [mat.name if mat else '' for mat in evaluated_mesh.materials]
skirt_ids = {i for i, name in enumerate(material_names) if name in SKIRT_MATERIALS}
collider_ids = {i for i, name in enumerate(material_names) if name in COLLIDER_MATERIALS}
if not skirt_ids:
    evaluated.to_mesh_clear()
    raise RuntimeError('No skirt material slots found')
if not collider_ids:
    evaluated.to_mesh_clear()
    raise RuntimeError('No skin material slot found for collision')

def filtered_mesh(name, keep_ids):
    mesh = evaluated_mesh.copy()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    remove = [face for face in bm.faces if face.material_index not in keep_ids]
    if remove:
        bmesh.ops.delete(bm, geom=remove, context='FACES')
    loose = [vert for vert in bm.verts if not vert.link_faces]
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

body_mesh = filtered_mesh('CLOTH_REBUILD_BODY_STATIC_MESH', set(range(len(material_names))) - skirt_ids)
cloth_mesh = filtered_mesh('CLOTH_REBUILD_SKIRT_MESH', skirt_ids)
collider_mesh = filtered_mesh('CLOTH_REBUILD_COLLIDER_MESH', collider_ids)

body = make_object('CLOTH_REBUILD_BODY_STATIC', body_mesh, root)
cloth_obj = make_object('CLOTH_REBUILD_SKIRT', cloth_mesh, root)
collider = make_object('CLOTH_REBUILD_BODY_COLLIDER', collider_mesh, b_support)

body['role'] = 'static posed character with original skirt faces removed'
cloth_obj['role'] = 'rendered skirt cloth simulation'
cloth_obj['source_frame'] = SOURCE_FRAME
collider['role'] = 'skin-only cloth collision surface'

# Keep the original armature-driven mesh as a hidden source, never delete it.
source['cloth_rebuild_original_hide_viewport'] = bool(source.hide_viewport)
source['cloth_rebuild_original_hide_render'] = bool(source.hide_render)
source.hide_viewport = True
source.hide_render = True

# The collider is evaluated but never rendered. Wire display keeps it inspectable without adding a solid duplicate.
collider.display_type = 'WIRE'
collider.hide_render = True
collider.hide_viewport = False

# Pin a narrow waist band. The current posed skirt spans roughly 0.33..1.32 m;
# a 12 cm upper band keeps the attachment stable while leaving the lower panels free.
coords = [vert.co.z for vert in cloth_obj.data.vertices]
min_z, max_z = min(coords), max(coords)
pin_threshold = max_z - 0.12
pin = cloth_obj.vertex_groups.new(name='CLOTH_PIN_WAIST')
pin_indices = [vert.index for vert in cloth_obj.data.vertices if vert.co.z >= pin_threshold]
if not pin_indices:
    raise RuntimeError('Pin group is empty')
all_pin_group_indices = [vert.index for vert in cloth_obj.data.vertices]
# Blender Cloth uses weight 1.0 as fully pinned; vertices outside the group are free.
pin.remove(all_pin_group_indices)
pin.add(pin_indices, 1.0, 'REPLACE')

cloth = cloth_obj.modifiers.new('CLOTH_REBUILD_SKIRT', 'CLOTH')
settings = cloth.settings
settings.quality = 6
settings.mass = 0.35
settings.air_damping = 5.0
settings.tension_stiffness = 18.0
settings.compression_stiffness = 18.0
settings.shear_stiffness = 8.0
settings.bending_stiffness = 0.45
settings.tension_damping = 5.0
settings.compression_damping = 5.0
settings.shear_damping = 5.0
settings.bending_damping = 2.0
settings.pin_stiffness = 1.0
settings.goal_default = 0.0
settings.goal_spring = 0.5
settings.vertex_group_mass = pin.name
settings.effector_weights.gravity = 1.0
if hasattr(settings, 'use_sewing_springs'):
    settings.use_sewing_springs = False
if hasattr(settings, 'use_internal_springs'):
    settings.use_internal_springs = False

collision = cloth.collision_settings
collision.use_collision = True
collision.use_self_collision = True
collision.distance_min = 0.018
collision.self_distance_min = 0.012
collision.damping = 0.35
collision.friction = 5.0
collision.self_friction = 5.0
collision.collision_quality = 4

collision_mod = collider.modifiers.new('CLOTH_REBUILD_COLLISION', 'COLLISION')

point_cache = cloth.point_cache
point_cache.frame_start = 1
point_cache.frame_end = PREVIEW_END
point_cache.frame_step = 1
point_cache.use_disk_cache = True
try:
    point_cache.filepath = os.path.join(CACHE_DIR, '')
except Exception:
    pass

scene.frame_start = 1
scene.frame_end = 250
scene.frame_set(1)

manifest = {
    'source': SOURCE_NAME,
    'source_frame': SOURCE_FRAME,
    'output': OUTPUT_PATH,
    'backup': BACKUP_PATH,
    'cache_dir': CACHE_DIR,
    'preview_frames': [1, PREVIEW_END],
    'skirt_materials': sorted(SKIRT_MATERIALS),
    'skirt_material_indices': sorted(skirt_ids),
    'skirt_vertices': len(cloth_obj.data.vertices),
    'skirt_faces': len(cloth_obj.data.polygons),
    'body_vertices': len(body.data.vertices),
    'body_faces': len(body.data.polygons),
    'collider_vertices': len(collider.data.vertices),
    'collider_faces': len(collider.data.polygons),
    'pin_vertices': len(pin_indices),
    'pin_threshold_z': pin_threshold,
    'gravity': list(scene.gravity),
    'cloth_quality': settings.quality,
    'collision_distance': collision.distance_min,
    'self_collision_distance': collision.self_distance_min,
}
manifest_path = os.path.join(CACHE_DIR, 'cloth_rebuild_manifest.json')
with open(manifest_path, 'w', encoding='utf-8') as handle:
    json.dump(manifest, handle, ensure_ascii=False, indent=2)

evaluated.to_mesh_clear()
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_PATH, check_existing=False)
print(json.dumps(manifest, ensure_ascii=False, indent=2))
