import bpy, json

result = {
    'active_workspace': bpy.context.window.workspace.name,
    'workspaces': [w.name for w in bpy.data.workspaces],
    'current_areas': [
        {'type': a.type, 'width': a.width, 'height': a.height}
        for a in bpy.context.screen.areas
    ],
}

anim = bpy.data.workspaces.get('动画') or bpy.data.workspaces.get('Animation')
if anim:
    screens = []
    for screen in anim.screens:
        screens.append({
            'screen': screen.name,
            'areas': [{'type': a.type, 'width': a.width, 'height': a.height} for a in screen.areas],
        })
    result['animation_screens'] = screens

print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
