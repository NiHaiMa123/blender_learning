import bpy
import json


out = {}
for name in ['左手套', '右手套']:
    obj = bpy.data.objects[name]
    out[name] = [
        {
            'name': m.name,
            'type': m.type,
            'object': getattr(getattr(m, 'object', None), 'name', None),
            'use_deform_preserve_volume': getattr(m, 'use_deform_preserve_volume', None),
        }
        for m in obj.modifiers
    ]
print(json.dumps(out, ensure_ascii=False, indent=2))
