import bpy

obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
if obj is None:
    raise RuntimeError("Character mesh not found")
mesh = obj.data
active = mesh.uv_layers.active
backup = mesh.uv_layers.get("Codex UV Backup Before Right Leg Mirror")
if active is None or backup is None:
    raise RuntimeError("Leg UV backup layer not found")

for source, target in zip(backup.data, active.data):
    target.uv = source.uv
mesh.update()
backup_index = next(index for index, layer in enumerate(mesh.uv_layers) if layer == backup)
mesh.uv_layers.remove(backup)
obj.pop("codex_right_leg_uv_mirror", None)
obj.pop("codex_right_leg_uv_mirror_faces", None)
print("Restored original UVMap and removed mirror backup")
