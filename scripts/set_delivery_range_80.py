import bpy

scene = bpy.context.scene
obj = bpy.data.objects.get('CLOTH_REBUILD_SKIRT')
mod = obj.modifiers.get('CLOTH_REBUILD_SKIRT') if obj else None
pc = mod.point_cache if mod else None
scene.frame_start = 1
scene.frame_end = 80
scene.frame_set(80)
bpy.ops.wm.save_mainfile()
print('SCENE_RANGE|scene=[%s,%s] cache=[%s,%s] baked=%s' % (
    scene.frame_start, scene.frame_end,
    pc.frame_start if pc else None, pc.frame_end if pc else None,
    pc.is_baked if pc else None))
