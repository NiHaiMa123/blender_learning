import bpy
import json
import os

batch_dir = r"D:\project\blender_learning\renders\今汐_4K_front_back_face_20260905_220943"
names = ("01_front_full_4k.png", "02_back_full_4k.png", "03_face_front_4k.png")
images = []
for name in names:
    path = os.path.join(batch_dir, name)
    image = bpy.data.images.load(path, check_existing=False)
    images.append(image)

report = {
    "images": {name: list(image.size) for name, image in zip(names, images)},
    "active_scene": bpy.context.scene.name,
    "active_camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
    "lantern_visibility": {
        name: bpy.data.objects[name].hide_render
        for name in ("Lantern_A", "Lantern_B", "Lantern_C")
        if bpy.data.objects.get(name)
    },
}
print(json.dumps(report, ensure_ascii=False, indent=2))
for image in images:
    bpy.data.images.remove(image)
