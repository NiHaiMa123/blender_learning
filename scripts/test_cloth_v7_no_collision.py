import bpy
import json

scene = bpy.context.scene
cloth_obj = bpy.data.objects['CLOTH_REBUILD_SKIRT']
cloth = next(mod for mod in cloth_obj.modifiers if mod.type == 'CLOTH')

scene.frame_set(1)
for obj in bpy.context.selected_objects:
    obj.select_set(False)
cloth_obj.hide_viewport = False
cloth_obj.hide_render = False
cloth_obj.select_set(True)
bpy.context.view_layer.objects.active = cloth_obj

window = bpy.context.window
area = next((item for item in window.screen.areas if item.type == 'VIEW_3D'), None)
region = next((item for item in area.regions if item.type == 'WINDOW'), None) if area else None
override = {'window': window, 'screen': window.screen}
if area and region:
    override.update({'area': area, 'region': region})
with bpy.context.temp_override(**override):
    bpy.ops.ptcache.free_bake_all()

cloth.collision_settings.use_collision = False
cloth.collision_settings.use_self_collision = False
cloth.point_cache.frame_start = 1
cloth.point_cache.frame_end = 80
cloth.point_cache.use_disk_cache = False

with bpy.context.temp_override(**override):
    bpy.ops.ptcache.bake_all()

scene.frame_set(80)
evaluated = cloth_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh = evaluated.to_mesh()
coords = [vertex.co for vertex in mesh.vertices]
summary = {
    'baked': cloth.point_cache.is_baked,
    'collision': cloth.collision_settings.use_collision,
    'vertices': len(coords),
    'min_z': min(co.z for co in coords),
    'max_z': max(co.z for co in coords),
}
evaluated.to_mesh_clear()
bpy.ops.wm.save_as_mainfile(filepath=r'D:\software\blender\project\今汐_cloth_rebuild_pose_v7_nocollision.blend')
print('V7_NO_COLLISION|' + json.dumps(summary, ensure_ascii=False))
