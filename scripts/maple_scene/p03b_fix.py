exec(open(r'D:/project/blender_learning/scripts/maple_scene/_common.py', encoding='utf-8').read())

# 1) nuke PLACEHOLDER collection entirely (dup .001/.002 objects included)
ph = bpy.data.collections.get('PLACEHOLDER')
if ph:
    for o in list(ph.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(ph)
# prefix sweep just in case
for o in list(bpy.data.objects):
    if o.name.startswith('PH_'):
        bpy.data.objects.remove(o, do_unlink=True)
# keep a simple ground for now
bpy.ops.mesh.primitive_plane_add(size=80)
g = bpy.context.object; g.name = 'PH_ground'; move_to_col(g, col('GROUND'))

# 2) unexclude LEAF_SRC, park leaf sources far underground (invisible, still in depsgraph)
lc = bpy.context.view_layer.layer_collection.children.get('LEAF_SRC')
if lc:
    lc.exclude = False
for o in bpy.data.collections['LEAF_SRC'].objects:
    o.location.z = -60

save()
render_preview('p03b_tree_eevee.png', pct=50)
