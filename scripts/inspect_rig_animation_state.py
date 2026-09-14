import bpy, json

arm = bpy.data.objects['卡提希娅_arm']
anim = arm.animation_data
result = {
    'mode': arm.mode,
    'show_in_front': arm.show_in_front,
    'action': anim.action.name if anim and anim.action else None,
    'nla_tracks': len(anim.nla_tracks) if anim else 0,
    'frame_range': [bpy.context.scene.frame_start, bpy.context.scene.frame_end],
    'auto_key': bpy.context.scene.tool_settings.use_keyframe_insert_auto,
    'bone_collections': [
        {'name': c.name, 'visible': c.is_visible, 'bones': len(c.bones)}
        for c in arm.data.collections
    ],
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
