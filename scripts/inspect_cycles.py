import bpy

print("cycles_addon_enabled", "cycles" in bpy.context.preferences.addons)
print("cycles_build", bpy.app.build_options.cycles)
try:
    bpy.context.scene.render.engine = "CYCLES"
    print("set_engine", bpy.context.scene.render.engine)
except Exception as exc:
    print("set_engine_error", repr(exc))
try:
    import _cycles
    print("cycles_devices", _cycles.available_devices(""))
except Exception as exc:
    print("devices_error", repr(exc))
