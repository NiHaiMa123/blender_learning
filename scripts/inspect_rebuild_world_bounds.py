import bpy
from mathutils import Vector
for name in ['CLOTH_REBUILD_BODY_STATIC', 'CLOTH_REBUILD_SKIRT', 'CLOTH_REBUILD_BODY_COLLIDER']:
    o = bpy.data.objects.get(name)
    if not o:
        continue
    mins = [1e9]*3
    maxs = [-1e9]*3
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        for i in range(3):
            mins[i] = min(mins[i], w[i])
            maxs[i] = max(maxs[i], w[i])
    print('BOUND|%s|parent=%s|matrix_loc=%s|min=%s|max=%s' % (name, o.parent.name if o.parent else None, tuple(round(x,3) for x in o.matrix_world.translation), tuple(round(x,3) for x in mins), tuple(round(x,3) for x in maxs)))
