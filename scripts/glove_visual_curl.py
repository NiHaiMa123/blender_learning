import bpy,math
from mathutils import Quaternion
a=bpy.data.objects['达妮娅_arm'];orig=bpy.app.driver_namespace['glove_verified_pose_channels']
for s in ['L','R']:
 for f in ['人指','中指','薬指','小指']:
  for j,deg in zip(['１','２','３'],[50,65,35]):
   p=a.pose.bones[f+j+'.'+s];p.rotation_quaternion=orig[p.name][1]@Quaternion((1,0,0),math.radians(deg))
 for f,deg in [('親指１',20),('親指２',25)]:
  p=a.pose.bones[f+'.'+s];p.rotation_quaternion=orig[p.name][1]@Quaternion((1,0,0),math.radians(deg))
bpy.context.view_layer.update()
for ar in bpy.context.screen.areas:ar.tag_redraw()
