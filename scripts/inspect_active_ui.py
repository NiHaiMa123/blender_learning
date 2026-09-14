import bpy, json
window = bpy.context.window
result = {
    'workspace': window.workspace.name,
    'screen': window.screen.name,
    'workspace_screens': [s.name for s in window.workspace.screens],
    'areas': [{'type': a.type, 'width': a.width, 'height': a.height} for a in window.screen.areas],
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
