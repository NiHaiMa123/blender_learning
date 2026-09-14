import bpy
import json


ARMATURE_NAME = "卡提希娅_arm"
arm = bpy.data.objects[ARMATURE_NAME]

keywords = (
    "腕", "ひじ", "肘", "手首", "手ＩＫ", "手IK", "腕ＩＫ", "腕IK",
    "肩", "手", "arm", "elbow", "wrist", "shoulder", "ik"
)

report = {
    "object": arm.name,
    "mode": arm.mode,
    "collections": [],
    "candidate_bones": [],
    "ik_constraints": [],
}

for col in arm.data.collections:
    report["collections"].append({
        "name": col.name,
        "visible": col.is_visible,
        "bones": [b.name for b in col.bones if any(k.lower() in b.name.lower() for k in keywords)],
    })

for b in arm.data.bones:
    if any(k.lower() in b.name.lower() for k in keywords):
        pb = arm.pose.bones[b.name]
        report["candidate_bones"].append({
            "name": b.name,
            "parent": b.parent.name if b.parent else None,
            "children": [c.name for c in b.children],
            "deform": b.use_deform,
            "head_local": list(b.head_local),
            "tail_local": list(b.tail_local),
            "locks_location": list(pb.lock_location),
            "locks_rotation": list(pb.lock_rotation),
            "locks_scale": list(pb.lock_scale),
            "constraints": [
                {
                    "name": c.name,
                    "type": c.type,
                    "target": c.target.name if getattr(c, "target", None) else None,
                    "subtarget": getattr(c, "subtarget", None),
                    "pole_subtarget": getattr(c, "pole_subtarget", None),
                    "chain_count": getattr(c, "chain_count", None),
                    "influence": c.influence,
                }
                for c in pb.constraints
            ],
        })

for pb in arm.pose.bones:
    for c in pb.constraints:
        if c.type == "IK":
            report["ik_constraints"].append({
                "owner": pb.name,
                "name": c.name,
                "target": c.target.name if c.target else None,
                "subtarget": c.subtarget,
                "pole_target": c.pole_target.name if c.pole_target else None,
                "pole_subtarget": c.pole_subtarget,
                "pole_angle": c.pole_angle,
                "chain_count": c.chain_count,
                "influence": c.influence,
                "iterations": c.iterations,
            })

print(json.dumps(report, ensure_ascii=False, indent=2))
