import bpy
obj = bpy.data.objects['CLOTH_REBUILD_BODY_COLLIDER']
print('MODS|' + str([(m.name, m.type, m.show_viewport, m.show_render) for m in obj.modifiers]))
col = getattr(obj, 'collision', None)
print('COLLISION_OBJ|' + str(type(col)))
if col:
    print('COLLISION_OBJ_ATTRS|' + ','.join(a for a in dir(col) if not a.startswith('_')))
    for a in ['use_culling', 'use_normal', 'damping', 'thickness_outer', 'thickness_inner', 'cloth_friction']:
        print('COL|%s=%s' % (a, getattr(col, a, 'N/A')))
