import bpy
s = bpy.context.scene
print("before", s.render.image_settings.file_format)
try:
    s.render.image_settings.file_format = 'PNG'
    print("after", s.render.image_settings.file_format)
except Exception as exc:
    print("set image_settings failed", repr(exc))
try:
    s.render.file_format = 'PNG'
    print("render.file_format", s.render.file_format)
except Exception as exc:
    print("set render failed", repr(exc))
