import bpy,collections,json
o=bpy.data.objects['达妮娅_mesh']
c=collections.Counter(p.material_index for p in o.data.polygons if max(o.data.vertices[i].co.z for i in p.vertices)<.3)
print('LOW_MATS',[(i,o.data.materials[i].name,n) for i,n in c.items()])
bpy.ops.screen.screenshot(filepath='D:/project/blender_learning/validation/shoe_fix_20260909/before.png')
