"""Final Cycles render of folded-card canopy."""
import bpy, sys, os
sys.path.insert(0, r'D:/project/blender_learning/scripts/maple_scene')
from _common import save, RENDER_DIR

s = bpy.context.scene
s.render.engine = 'CYCLES'
s.render.resolution_percentage = 100
s.render.filepath = os.path.join(RENDER_DIR, 'p09e_fold_cycles.png')
bpy.ops.render.render(write_still=True)
print('CYCLES DONE', s.render.filepath)
