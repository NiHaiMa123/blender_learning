import bpy, json

scene = bpy.data.scenes['Codex_Cycles_Render']
result = {
    'scene': scene.name,
    'objects': [
        {
            'name': o.name,
            'type': o.type,
            'parent': o.parent.name if o.parent else None,
            'collections': [c.name for c in o.users_collection],
        }
        for o in scene.objects
    ],
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
