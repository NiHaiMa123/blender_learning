import bpy, math, os, random
from mathutils import Vector

ROOT = r'D:/project/blender_learning'
RENDER_DIR = os.path.join(ROOT, 'renders', 'maple')
os.makedirs(RENDER_DIR, exist_ok=True)
BLEND_PATH = os.path.join(ROOT, 'maple_scene.blend')

def col(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def move_to_col(obj, c):
    for uc in list(obj.users_collection):
        uc.objects.unlink(obj)
    c.objects.link(obj)

def save():
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print('SAVED', BLEND_PATH)

def render_preview(name, engine='BLENDER_EEVEE_NEXT', pct=50):
    s = bpy.context.scene
    old_engine, old_pct = s.render.engine, s.render.resolution_percentage
    try:
        s.render.engine = engine
    except Exception:
        try:
            s.render.engine = 'BLENDER_EEVEE'
        except Exception:
            s.render.engine = 'BLENDER_WORKBENCH'
    s.render.image_settings.file_format = 'PNG'
    s.render.resolution_percentage = pct
    s.render.filepath = os.path.join(RENDER_DIR, name)
    bpy.ops.render.render(write_still=True)
    s.render.engine, s.render.resolution_percentage = old_engine, old_pct
    print('RENDERED', s.render.filepath)

def new_principled(name, base_color, rough=0.8):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*base_color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    return m
