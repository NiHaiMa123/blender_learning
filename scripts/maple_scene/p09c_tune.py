"""Tune card canopy: richer red (less emission wash), slightly denser, Cycles render."""
import bpy, sys
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import save, render_preview, RENDER_DIR
import os

m = bpy.data.materials['MapleCard']
nt = m.node_tree
bsdf = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
bsdf.inputs['Emission Strength'].default_value = 0.35
hue = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeHueSaturation')
hue.inputs['Saturation'].default_value = 1.5
for n in nt.nodes:
    if n.bl_idname == 'ShaderNodeMapRange':
        if abs(n.inputs['To Min'].default_value - 1.0) < 0.01:
            n.inputs['To Min'].default_value = 0.9
            n.inputs['To Max'].default_value = 1.15

g = bpy.data.node_groups['GN_CardCanopy']
dp = next(n for n in g.nodes if n.bl_idname == 'GeometryNodeDistributePointsOnFaces')
if dp.inputs.get('Density Max'):
    dp.inputs['Density Max'].default_value = 9.0
rs = next(n for n in g.nodes if n.bl_idname == 'FunctionNodeRandomValue' and n.data_type == 'FLOAT')
rs.inputs['Min'].default_value = 0.14
rs.inputs['Max'].default_value = 0.26

save()
# final-ish Cycles render for comparison
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 100
s.render.filepath = os.path.join(RENDER_DIR, 'p09c_card_cycles.png')
bpy.ops.render.render(write_still=True)
print('CYCLES DONE', s.render.filepath)
