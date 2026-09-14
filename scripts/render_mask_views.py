import bpy
import os
from mathutils import Vector

# Non-destructive mask viewer: temporarily pipe a mask scalar into an
# emission shader so we can SEE exactly where the lift / gold masks fire.
mat = bpy.data.materials.get("皮肤")
tree = mat.node_tree
output = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
z_in = tree.nodes.get("Codex Band Lift Z In")
z_out = tree.nodes.get("Codex Band Lift Z Out")
x_feather = tree.nodes.get("Codex Band Lift X Feather")
geo_z = tree.nodes.get("Codex Band Lift Geometry Z")
geo_all = tree.nodes.get("Codex Band Lift Geometry All")
not_gold = tree.nodes.get("Codex Band Lift Not Gold")
if not all([z_in, z_out, x_feather, geo_z, geo_all, not_gold]):
    raise RuntimeError("band lift sub-nodes missing")

orig_link = next((l for l in tree.links
                  if l.to_node == output and l.to_socket.name == "Surface"), None)
orig_from = (orig_link.from_node, orig_link.from_socket.name) if orig_link else None

emit = tree.nodes.new("ShaderNodeEmission")
emit.name = "Codex Debug Mask Viewer"
emit.location = (1400, -300)

scene = bpy.context.scene
camera = scene.camera
out_dir = r"D:\project\blender_learning\renders\_preview_right_leg_uv_1080p"

old_transform = (camera.location.copy(), camera.rotation_mode,
                 camera.rotation_euler.copy(), camera.rotation_quaternion.copy(),
                 camera.data.lens, camera.data.sensor_fit)
old_render = (scene.render.engine, scene.render.resolution_x, scene.render.resolution_y,
              scene.render.resolution_percentage, scene.render.filepath,
              scene.cycles.samples, scene.cycles.use_denoising,
              scene.cycles.use_adaptive_sampling)
old_camera = scene.camera


def aim_at(target):
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = (Vector(target) - camera.location).to_track_quat("-Z", "Y")


jobs = [("maskview_zin.png", z_in, 0),
        ("maskview_zout.png", z_out, 0),
        ("maskview_x.png", x_feather, 0),
        ("maskview_geoz.png", geo_z, 0),
        ("maskview_geoall.png", geo_all, 0),
        ("maskview_notgold.png", not_gold, 0)]
try:
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 40
    scene.render.image_settings.file_format = "PNG"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    camera.location = Vector((0.0, -1.82, 0.72))
    camera.data.lens = 85.0
    camera.data.sensor_fit = "VERTICAL"
    aim_at(Vector((-0.02, 0.02, 0.72)))

    for filename, node, out_idx in jobs:
        for link in list(tree.links):
            if link.to_node == output and link.to_socket.name == "Surface":
                tree.links.remove(link)
        tree.links.new(node.outputs[out_idx], emit.inputs["Color"])
        tree.links.new(emit.outputs["Emission"], output.inputs["Surface"])
        scene.render.filepath = os.path.join(out_dir, filename)
        bpy.ops.render.render(write_still=True)
finally:
    for link in list(tree.links):
        if link.to_node == output and link.to_socket.name == "Surface":
            tree.links.remove(link)
    if orig_from is not None:
        tree.links.new(orig_from[0].outputs[orig_from[1]], output.inputs["Surface"])
    tree.nodes.remove(emit)
    camera.location = old_transform[0]
    camera.rotation_mode = "QUATERNION"
    camera.rotation_quaternion = old_transform[3]
    camera.rotation_mode = old_transform[1]
    if old_transform[1] != "QUATERNION":
        camera.rotation_euler = old_transform[2]
    camera.data.lens, camera.data.sensor_fit = old_transform[4], old_transform[5]
    (scene.render.engine, scene.render.resolution_x, scene.render.resolution_y,
     scene.render.resolution_percentage, scene.render.filepath,
     scene.cycles.samples, scene.cycles.use_denoising,
     scene.cycles.use_adaptive_sampling) = old_render
    scene.camera = old_camera

print("mask views done")
