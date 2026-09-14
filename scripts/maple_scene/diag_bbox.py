import bpy
from mathutils import Vector
fog = bpy.data.objects['FogCube']
bb = [fog.matrix_world @ Vector(c) for c in fog.bound_box]
xs = [v.x for v in bb]; ys = [v.y for v in bb]; zs = [v.z for v in bb]
print('fog bounds x:', min(xs), max(xs), 'y:', min(ys), max(ys), 'z:', min(zs), max(zs))
cam = bpy.data.objects['Camera']
print('cam:', tuple(cam.location))
pv = next(n for n in bpy.data.materials['FogVol'].node_tree.nodes if n.bl_idname == 'ShaderNodeVolumePrincipled')
print('density:', pv.inputs['Density'].default_value)
