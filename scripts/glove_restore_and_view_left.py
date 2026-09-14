import bpy
from mathutils import Vector
a=bpy.data.objects['达妮娅_arm'];orig=bpy.app.driver_namespace['glove_verified_pose_channels']
for n,(loc,q,e,ax,sc) in orig.items():
 p=a.pose.bones[n];p.location=loc;p.rotation_quaternion=q;p.rotation_euler=e;p.rotation_axis_angle=ax;p.scale=sc
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  sp=area.spaces.active;r=sp.region_3d
  bpy.app.driver_namespace['glove_view_original']=(r.view_location.copy(),r.view_rotation.copy(),r.view_distance,sp.overlay.show_overlays)
  r.view_location=(a.pose.bones['手首.L'].head+a.pose.bones['中指３.L'].tail)*.5
  r.view_distance=.29;sp.overlay.show_overlays=False
bpy.context.view_layer.update()
for ar in bpy.context.screen.areas:ar.tag_redraw()
