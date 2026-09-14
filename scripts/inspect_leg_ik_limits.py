import bpy, json

arm = bpy.data.objects['卡提希娅_arm']
result = {}
for side in ('R', 'L'):
    pb = arm.pose.bones[f'ひざ.{side}']
    c = next((x for x in pb.constraints if x.type == 'LIMIT_ROTATION'), None)
    result[side] = {
        'ik_limits': {
            axis: {
                'use': getattr(pb, f'use_ik_limit_{axis}'),
                'min': getattr(pb, f'ik_min_{axis}'),
                'max': getattr(pb, f'ik_max_{axis}'),
                'stiffness': getattr(pb, f'ik_stiffness_{axis}'),
                'lock': getattr(pb, f'lock_ik_{axis}'),
            }
            for axis in ('x', 'y', 'z')
        },
        'limit_constraint': None if c is None else {
            'owner_space': c.owner_space,
            'use_limit_x': c.use_limit_x,
            'min_x': c.min_x,
            'max_x': c.max_x,
            'use_limit_y': c.use_limit_y,
            'min_y': c.min_y,
            'max_y': c.max_y,
            'use_limit_z': c.use_limit_z,
            'min_z': c.min_z,
            'max_z': c.max_z,
        },
    }
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
