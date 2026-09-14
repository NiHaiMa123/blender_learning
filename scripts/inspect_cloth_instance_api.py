import bpy
mesh = bpy.data.objects.get('CLOTH_REBUILD_SKIRT')
if mesh and mesh.modifiers:
    mod = mesh.modifiers.get('CLOTH_REBUILD_SKIRT')
    print('MOD_TYPE|' + str(type(mod)))
    print('SETTINGS_TYPE|' + str(type(mod.settings)))
    print('COLLISION_TYPE|' + str(type(mod.collision_settings)))
    print('COLLISION_DIR|' + ','.join(a for a in dir(mod.collision_settings) if not a.startswith('_')))
    print('MOD_DIR|' + ','.join(a for a in dir(mod) if 'collision' in a.lower() or 'self' in a.lower()))
