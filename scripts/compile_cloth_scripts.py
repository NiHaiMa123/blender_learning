from pathlib import Path

root = Path(r'D:\project\blender_learning\scripts')
names = [
    'audit_cloth_live.py',
    'test_cloth_correct_pin_v4.py',
    'render_cloth_correct_pin_preview_v4.py',
    'bake_cloth_final_v3.py',
    'validate_cloth_final.py',
    'reopen_validate_cloth_final.py',
    'build_cloth_rebuild_v1.py',
    'test_cloth_outer_stable_v3.py',
    'bake_cloth_direct_debug.py',
    'bake_cloth_preview_v1.py',
    'bake_cloth_verified_preview_v2.py',
    'test_cloth_case_b_persist.py',
    'test_cloth_collision_v2.py',
    'test_cloth_component_pin_v2.py',
    'test_cloth_outer_self_v3.py',
    'test_cloth_stability_v2.py',
    'test_cloth_pin_weights_v1.py',
]
for name in names:
    path = root / name
    compile(path.read_text(encoding='utf-8-sig'), str(path), 'exec')
print('COMPILE_CLOTH_SCRIPTS|ok=%d' % len(names))
