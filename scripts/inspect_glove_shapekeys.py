import bpy
import json


out = {}
for name in ['左手套', '右手套']:
    obj = bpy.data.objects[name]
    out[name] = {
        'shape_keys': len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0,
        'nonzero': [
            {'name': key.name, 'value': key.value}
            for key in obj.data.shape_keys.key_blocks
            if abs(key.value) > 1e-7
        ] if obj.data.shape_keys else [],
    }
print(json.dumps(out, ensure_ascii=False, indent=2))
