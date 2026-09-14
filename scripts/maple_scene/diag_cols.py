import bpy, json
out = {}
for lc in bpy.context.scene.view_layers['ViewLayer'].layer_collection.children:
    out[lc.name] = {'exclude': lc.exclude, 'hide_vp': lc.hide_viewport}
print('COLS ' + json.dumps(out, ensure_ascii=False))
