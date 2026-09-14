import bpy

# Remove the leg ring visually (non-destructive, reversible):
# 1. metal leg -> fully transparent (nodes kept; re-run
#    fix_ring_contact_shadow.py to restore the ring).
# 2. Bypass baked-ring metal overlay on skin so contact tint under the
#    former ring renders as plain lifted skin, like the left leg
#    (re-run apply_baked_ring_metal_overlay.py to restore).

metal = bpy.data.materials.get("metal leg")
if metal is None or not metal.use_nodes or not metal.node_tree:
    raise RuntimeError("metal leg material not found")
mtree = metal.node_tree
mout = next((n for n in mtree.nodes if n.type == "OUTPUT_MATERIAL"), None)
trans = mtree.nodes.get("Codex Ring Shadow Transparent")
if mout is None or trans is None:
    raise RuntimeError("metal leg nodes not found")
for link in list(mtree.links):
    if link.to_node == mout and link.to_socket.name == "Surface":
        mtree.links.remove(link)
mtree.links.new(trans.outputs["BSDF"], mout.inputs["Surface"])
metal["codex_ring_removed"] = "hidden_transparent"

skin = bpy.data.materials.get("皮肤")
if skin is None or not skin.use_nodes or not skin.node_tree:
    raise RuntimeError("skin material not found")
stree = skin.node_tree
sout = next((n for n in stree.nodes if n.type == "OUTPUT_MATERIAL"), None)
principled = stree.nodes.get("Skin Principled")
if sout is None or principled is None:
    raise RuntimeError("skin shader nodes not found")
for link in list(stree.links):
    if link.to_node == sout and link.to_socket.name == "Surface":
        stree.links.remove(link)
stree.links.new(principled.outputs["BSDF"], sout.inputs["Surface"])
skin["codex_baked_ring_disabled"] = "bypass_for_ring_removal"

print("leg ring hidden; skin overlay bypassed")
