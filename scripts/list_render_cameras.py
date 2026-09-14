import bpy
scene = bpy.context.scene
print('ACTIVE|' + str(scene.camera.name if scene.camera else None))
for o in bpy.data.objects:
    if o.type == 'CAMERA':
        print('CAM|%s|loc=%s|rot=%s|lens=%.1f' % (o.name, tuple(round(x, 3) for x in o.location), tuple(round(x, 3) for x in o.rotation_euler), o.data.lens))
