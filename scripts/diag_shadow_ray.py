import bpy
import json
from mathutils import Vector

# Raycast from strip/upper-thigh skin points toward key lights to find
# which geometry blocks the light (= the shadow caster).
deps = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene

origins = {
    "strip_below_ring": Vector((-0.10, -0.055, 0.665)),
    "bandT_above_ring": Vector((-0.10, -0.055, 0.755)),
    "plain_below": Vector((-0.10, -0.055, 0.58)),
}
targets = {
    "Key_Soft": Vector((-2.4, -3.2, 3.6)),
    "Fill_Front": Vector((2.8, -3.4, 1.8)),
    "Metal_Strip_Key": Vector((-1.25, -2.0, 2.55)),
}

results = {}
for oname, origin in origins.items():
    results[oname] = {}
    for lname, light_pos in targets.items():
        direction = (light_pos - origin).normalized()
        hit, loc, normal, index, obj, matrix = scene.ray_cast(deps, origin, direction)
        if hit:
            mat = None
            if obj.type == "MESH" and obj.data.polygons and index >= 0:
                try:
                    slot = obj.material_slots[obj.data.polygons[index].material_index]
                    mat = slot.material.name if slot.material else None
                except Exception:
                    pass
            results[oname][lname] = {
                "hit_obj": obj.name,
                "material": mat,
                "loc": [round(v, 4) for v in loc],
                "dist": round((loc - origin).length, 4),
            }
        else:
            results[oname][lname] = {"hit_obj": None}
print(json.dumps(results, ensure_ascii=False, indent=1))
