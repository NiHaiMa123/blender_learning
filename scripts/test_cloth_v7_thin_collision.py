import bpy
import json

scene = bpy.context.scene
cloth_obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
cloth = cloth_obj.modifiers['CLOTH_REBUILD_SKIRT']
collider = bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER']

scene.frame_set(1)
window = bpy.context.window
area = next((item for item in window.screen.areas if item.type == 'VIEW_3D'), None)
region = next((item for item in area.regions if item.type == 'WINDOW'), None) if area else None
override = {'window': window, 'screen': window.screen}
if area and region:
    override.update({'area': area, 'region': region})
with bpy.context.temp_override(**override):
    bpy.ops.ptcache.free_bake_all()

# A doubled/solidified skin shell trapped initially intersecting garment layers.
# Use the posed skin surface directly with only a small collision margin.
for modifier in list(collider.modifiers):
    if modifier.type == 'SOLIDIFY':
        collider.modifiers.remove(modifier)

body_collision = collider.collision
body_collision.use = True
body_collision.use_culling = False
body_collision.use_normal = False
body_collision.thickness_outer = 0.004
body_collision.thickness_inner = 0.002
body_collision.damping = 0.35
body_collision.cloth_friction = 1.0

collision = cloth.collision_settings
collision.use_collision = True
collision.use_self_collision = False
collision.collision_quality = 5
collision.distance_min = 0.002
collision.damping = 0.5
collision.friction = 0.2
cloth.point_cache.frame_start = 1
cloth.point_cache.frame_end = 80
cloth.point_cache.use_disk_cache = False

with bpy.context.temp_override(**override):
    bpy.ops.ptcache.bake_all()

scene.frame_set(80)
summary = {
    'baked': cloth.point_cache.is_baked,
    'cloth_distance': collision.distance_min,
    'outer': body_collision.thickness_outer,
    'inner': body_collision.thickness_inner,
    'solidify': any(mod.type == 'SOLIDIFY' for mod in collider.modifiers),
}
bpy.ops.wm.save_as_mainfile(filepath=r'D:\software\blender\project\今汐_cloth_rebuild_pose_v7_thincollision.blend')
print('V7_THIN_COLLISION|' + json.dumps(summary, ensure_ascii=False))
