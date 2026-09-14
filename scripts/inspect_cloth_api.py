import bpy
print('CLOTH_SETTINGS|' + ','.join(p.identifier for p in bpy.types.ClothSettings.bl_rna.properties))
print('COLLISION_SETTINGS|' + ','.join(p.identifier for p in bpy.types.CollisionSettings.bl_rna.properties))
print('POINT_CACHE|' + ','.join(p.identifier for p in bpy.types.PointCache.bl_rna.properties))
