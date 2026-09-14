import bpy, os, json

scene = bpy.data.scenes['Codex_Cycles_Render']
window = bpy.context.window
window.scene = scene

backup = r'D:\project\blender_learning\renders\before_environment_removal.blend'
output = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
os.makedirs(os.path.dirname(backup), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True, check_existing=False)

root = bpy.data.objects['Cartythia']
arm = bpy.data.objects['卡提希娅_arm']
mesh = bpy.data.objects['卡提希娅_mesh']

def is_descendant_of(obj, ancestor):
    current = obj
    while current is not None:
        if current == ancestor:
            return True
        current = current.parent
    return False

main_collection = bpy.data.collections.get('Codex_Character_Main')
if main_collection is None:
    main_collection = bpy.data.collections.new('Codex_Character_Main')
if main_collection.name not in [c.name for c in scene.collection.children]:
    scene.collection.children.link(main_collection)

physics_collection = bpy.data.collections.get('Codex_Character_Physics_Hidden')
if physics_collection is None:
    physics_collection = bpy.data.collections.new('Codex_Character_Physics_Hidden')
if physics_collection.name not in [c.name for c in scene.collection.children]:
    scene.collection.children.link(physics_collection)

main_objects = {root, arm, mesh}
character_objects = [o for o in bpy.data.objects if is_descendant_of(o, root)]
for obj in character_objects:
    target = main_collection if obj in main_objects else physics_collection
    if obj.name not in target.objects:
        target.objects.link(obj)

# Keep the imported physics assets recoverable but remove them from the
# animation viewport and final render until the user needs secondary motion.
physics_collection.hide_viewport = True
physics_collection.hide_render = True

# Unlink the shared living-room collection from this scene only.  The source
# scene and all datablocks remain intact.
removed_collections = []
protected = {main_collection, physics_collection}
for collection in list(scene.collection.children):
    if collection in protected:
        continue
    removed_collections.append(collection.name)
    scene.collection.children.unlink(collection)

# Restore imported/rest pose and discard any active animation evaluation.
for obj in bpy.context.view_layer.objects:
    obj.select_set(False)
arm.hide_set(False)
arm.hide_viewport = False
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if arm.mode == 'POSE':
    bpy.ops.object.mode_set(mode='OBJECT')

arm.animation_data_create()
arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis.identity()

action = bpy.data.actions.get('卡提希娅_K帧')
if action is None:
    action = bpy.data.actions.new('卡提希娅_K帧')
arm.animation_data.action = action
scene.frame_set(1)
bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode='POSE')

# Neutral background for clean posing and camera preview.
world = bpy.data.worlds.get('Codex_Animation_Neutral') or bpy.data.worlds.new('Codex_Animation_Neutral')
world.use_nodes = True
background = next((n for n in world.node_tree.nodes if n.type == 'BACKGROUND'), None)
if background is None:
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    output_node = next((n for n in world.node_tree.nodes if n.type == 'OUTPUT_WORLD'), None)
    if output_node is None:
        output_node = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'], output_node.inputs['Surface'])
background.inputs['Color'].default_value = (0.025, 0.028, 0.038, 1.0)
background.inputs['Strength'].default_value = 0.22
scene.world = world

# Frame the restored character in the large posing viewport.
for area in window.screen.areas:
    if area.type != 'VIEW_3D':
        continue
    space = area.spaces.active
    if space.region_3d.view_perspective != 'CAMERA':
        region = next((r for r in area.regions if r.type == 'WINDOW'), None)
        if region:
            try:
                with bpy.context.temp_override(window=window, screen=window.screen, area=area, region=region):
                    bpy.ops.view3d.view_selected(use_all_regions=False)
            except Exception:
                pass
    area.tag_redraw()

bpy.ops.wm.save_as_mainfile(filepath=output, copy=True, check_existing=False)

result = {
    'backup': backup,
    'saved': output,
    'removed_scene_collections': removed_collections,
    'main_objects': sorted(o.name for o in main_objects),
    'hidden_physics_objects': len(character_objects) - len(main_objects),
    'pose_mode': arm.mode,
    'action': action.name,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
