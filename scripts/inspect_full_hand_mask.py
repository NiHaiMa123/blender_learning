import bpy
import json


body = bpy.data.objects['达妮娅_mesh']
arm = bpy.data.objects['达妮娅_arm']


def weight_indices(side):
    names = [
        f'手首.{side}', f'手捩.{side}', f'手捩1.{side}', f'ダミー.{side}',
        f'親指０.{side}', f'親指１.{side}', f'親指２.{side}',
    ]
    for finger in ['人指', '中指', '薬指', '小指']:
        names += [f'{finger}{joint}.{side}' for joint in ['１', '２', '３']]
    return {body.vertex_groups[name].index for name in names if body.vertex_groups.get(name)}


out = {}
for side in ['L', 'R']:
    wrist = arm.data.bones['手首.' + side]
    axis = (wrist.tail_local - wrist.head_local).normalized()
    sign = 1 if side == 'L' else -1
    indices = weight_indices(side)
    selected = []
    for vertex in body.data.vertices:
        has_hand_weight = any(item.group in indices and item.weight > 0.001 for item in vertex.groups)
        in_region = sign * vertex.co.x > 0.25 and 0.70 < vertex.co.z < 1.20 and (vertex.co - wrist.head_local).dot(axis) > -0.08
        if has_hand_weight and in_region:
            selected.append(vertex.index)
    out[side] = {
        'count': len(selected),
        'min': [min(body.data.vertices[i].co[j] for i in selected) for j in range(3)] if selected else None,
        'max': [max(body.data.vertices[i].co[j] for i in selected) for j in range(3)] if selected else None,
    }
print(json.dumps(out, ensure_ascii=False, indent=2))
