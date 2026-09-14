import bpy
fog = bpy.data.objects['FogCube']
for attr in ('visible_camera', 'visible_shadow', 'visible_volume_scatter', 'hide_render',
             'hide_viewport', 'display_type', 'visible_get'):
    v = getattr(fog, attr, 'N/A')
    print(attr, v() if callable(v) else v)
s = bpy.context.scene
print('engine:', s.render.engine, 'device:', s.cycles.device)
# volume props on scene?
print('volume props:', [p for p in dir(s.cycles) if 'volume' in p.lower()])
