"""Fix: move CardLeaf out of LEAF_SRC (it leaked into falling/canopy pick
collections), brighten leaf material, add per-instance hue variation."""
import bpy, sys
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import col, move_to_col, save, render_preview

# 1. own collection + hide source object (instances unaffected by hide_render)
c = col('LEAF_CARD_SRC')
card = bpy.data.objects['CardLeaf']
move_to_col(card, c)
card.hide_render = True

# 2. material tune: brighter, more emission, hue varies red<->orange
m = bpy.data.materials['MapleCard']
nt = m.node_tree
bsdf = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled')
if bsdf.inputs.get('Emission Strength'):
    bsdf.inputs['Emission Strength'].default_value = 0.55
hue = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeHueSaturation')
hue.inputs['Saturation'].default_value = 1.35
mr = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange')
mr.inputs['To Min'].default_value = 1.0
mr.inputs['To Max'].default_value = 1.4

# per-instance hue jitter: reuse ObjectInfo Random -> second MapRange -> Hue
oi = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeObjectInfo')
mr2 = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeMapRange' and n != mr), None)
if not mr2:
    mr2 = nt.nodes.new('ShaderNodeMapRange')
mr2.inputs['From Min'].default_value = 0.0
mr2.inputs['From Max'].default_value = 1.0
mr2.inputs['To Min'].default_value = 0.10   # toward orange-red
mr2.inputs['To Max'].default_value = 0.20   # toward deep red
if not any(l.to_node == hue and l.to_socket == hue.inputs['Hue'] for l in nt.links):
    nt.links.new(oi.outputs['Random'], mr2.inputs['Value'])
    nt.links.new(mr2.outputs['Result'], hue.inputs['Hue'])

save()
render_preview('p09b_card_eevee.png', pct=50)
print('FIX DONE')
