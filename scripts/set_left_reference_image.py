import bpy, json

source = r'C:\Users\Administrator\AppData\Local\Temp\codex-clipboard-2048e31c-526f-408d-85c9-b36e7512100a.webp'
window = bpy.context.window
screen = window.screen

image = bpy.data.images.load(source, check_existing=True)
image.name = '参考图_女角色站姿'
if not image.packed_file:
    image.pack()

view_areas = sorted(
    [a for a in screen.areas if a.type == 'VIEW_3D'],
    key=lambda a: a.width * a.height,
)
if not view_areas:
    raise RuntimeError('No 3D viewport found')

left_area = view_areas[0]
left_area.type = 'IMAGE_EDITOR'
space = left_area.spaces.active
space.image = image
if hasattr(space, 'ui_mode'):
    space.ui_mode = 'VIEW'
if hasattr(space, 'show_region_ui'):
    space.show_region_ui = False
if hasattr(space, 'show_region_toolbar'):
    space.show_region_toolbar = False

region = next((r for r in left_area.regions if r.type == 'WINDOW'), None)
if region:
    try:
        with bpy.context.temp_override(window=window, screen=screen, area=left_area, region=region):
            bpy.ops.image.view_all(fit_view=True)
    except Exception:
        pass
left_area.tag_redraw()

path = r'D:\project\blender_learning\renders\carthya_character_only_keyframing.blend'
bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, check_existing=False)

result = {
    'area_type': left_area.type,
    'image': image.name,
    'size': list(image.size),
    'packed': bool(image.packed_file),
    'saved': path,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
return_value = result
