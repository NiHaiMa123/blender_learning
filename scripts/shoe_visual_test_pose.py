import bpy,math
from mathutils import Quaternion
arm=bpy.data.objects['达妮娅_arm']
if 'shoe_visual_test_original' not in bpy.app.driver_namespace:
    bpy.app.driver_namespace['shoe_visual_test_original']={p.name:p.rotation_quaternion.copy() for p in arm.pose.bones}
for s in ['L','R']:
    p=arm.pose.bones['足首D.'+s];p.rotation_quaternion=bpy.app.driver_namespace['shoe_visual_test_original'][p.name]@Quaternion((1,0,0),math.radians(25))
bpy.context.view_layer.update()
for a in bpy.context.screen.areas:a.tag_redraw()
print('Visual test: both ankles +25 degrees; original pose retained for restoration.')
