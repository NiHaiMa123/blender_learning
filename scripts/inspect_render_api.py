import bpy

scene = bpy.context.scene
print("render.filepath", scene.render.filepath)
print("image_settings.file_format", scene.render.image_settings.file_format)
print("file_format_items", [i.identifier for i in scene.render.image_settings.bl_rna.properties['file_format'].enum_items])
print("engine_items", [i.identifier for i in scene.render.bl_rna.properties['engine'].enum_items])
print("has ffmpeg", hasattr(scene.render, 'ffmpeg'))
