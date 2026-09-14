import bpy

# Tone down street lamp points so heads stay readable (idempotent).
ENERGY = 400.0
done = []
coll = bpy.data.collections.get("路灯")
if coll is not None:
    for o in coll.all_objects:
        if o.type == "LIGHT":
            o.data.energy = ENERGY
            done.append(o.name)

for o in bpy.data.objects:
    if o.type == "LIGHT" and o.name.startswith("点光.00"):
        o.data.energy = ENERGY
        if o.name not in done:
            done.append(o.name)

bpy.data.collections["路灯"]["codex_lamp_energy"] = ENERGY
print(f"lamp energy -> {ENERGY}: {sorted(done)}")
