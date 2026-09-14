import bpy, json

window = bpy.context.window
workspace = bpy.data.workspaces.get('动画') or bpy.data.workspaces.get('Animation')
if workspace is None:
    raise RuntimeError('Animation workspace not found')
window.workspace = workspace

scene = bpy.data.scenes['Codex_Cycles_Render']
window.scene = scene
scene.frame_start = 1
scene.frame_end = 120
scene.frame_set(1)
scene.tool_settings.use_keyframe_insert_auto = False

arm = bpy.data.objects['卡提希娅_arm']
arm.hide_set(False)
arm.hide_viewport = False
arm.show_in_front = True

# Body posing first: keep secondary-motion collections available but hidden.
hidden_collections = {'髪', 'リボン', 'スカート'}
for collection in arm.data.collections:
    if collection.name in hidden_collections:
        collection.is_visible = False

# Prepare a clean action without inserting any keys on the user's behalf.
arm.animation_data_create()
if arm.animation_data.action is None:
    action = bpy.data.actions.get('卡提希娅_K帧') or bpy.data.actions.new('卡提希娅_K帧')
    arm.animation_data.action = action
else:
    action = arm.animation_data.action

# Make the rig active and enter Pose Mode.
for obj in bpy.context.view_layer.objects:
    obj.select_set(False)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if arm.mode != 'POSE':
    bpy.ops.object.mode_set(mode='POSE')

screen = window.screen
view_areas = sorted(
    [a for a in screen.areas if a.type == 'VIEW_3D'],
    key=lambda a: a.width * a.height,
)

for index, area in enumerate(view_areas):
    space = area.spaces.active
    space.shading.type = 'MATERIAL'
    space.show_gizmo = True
    if index == 0 and len(view_areas) > 1:
        # Smaller viewport: clean camera/composition preview.
        space.region_3d.view_perspective = 'CAMERA'
        space.overlay.show_overlays = False
    else:
        # Larger viewport: interactive bone posing.
        space.region_3d.view_perspective = 'PERSP'
        space.overlay.show_overlays = True
        if hasattr(space.overlay, 'show_relationship_lines'):
            space.overlay.show_relationship_lines = False
        if hasattr(space.overlay, 'show_motion_paths'):
            space.overlay.show_motion_paths = True

for area in screen.areas:
    if area.type == 'DOPESHEET_EDITOR' and area.height > 80:
        space = area.spaces.active
        space.mode = 'ACTION'
        if hasattr(space.dopesheet, 'show_only_selected'):
            space.dopesheet.show_only_selected = True
        if hasattr(space, 'show_region_ui'):
            space.show_region_ui = True
    elif area.type == 'OUTLINER':
        area.spaces.active.display_mode = 'VIEW_LAYER'
    elif area.type == 'PROPERTIES':
        try:
            area.spaces.active.context = 'DATA'
        except Exception:
            pass

result = {
    'workspace': workspace.name,
    'scene': scene.name,
    'mode': arm.mode,
    'action': action.name,
    'frame_range': [scene.frame_start, scene.frame_end],
    'auto_key': scene.tool_settings.use_keyframe_insert_auto,
    'hidden_bone_collections': sorted(hidden_collections),
    'areas': [{'type': a.type, 'width': a.width, 'height': a.height} for a in screen.areas],
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
