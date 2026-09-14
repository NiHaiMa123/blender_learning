import bpy, json
scene = bpy.data.scenes['Codex_Cycles_Render']
result = {
    'root_objects': [o.name for o in scene.collection.objects],
    'child_collections': [
        {'name': c.name, 'objects': len(c.objects), 'children': [cc.name for cc in c.children]}
        for c in scene.collection.children
    ],
    'rigidbody_collection': scene.rigidbody_world.collection.name if scene.rigidbody_world and scene.rigidbody_world.collection else None,
    'constraint_collection': scene.rigidbody_world.constraints.name if scene.rigidbody_world and scene.rigidbody_world.constraints else None,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
