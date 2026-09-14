"""Extract packed leaf/bark textures via packed_file.data + dump material links"""
import bpy, os, json

OUT = r'D:/project/blender_learning/scripts/asset_tex'
os.makedirs(OUT, exist_ok=True)

want = ['iBushes-Petal', 'opacity', 'Map #60', 'bark_diffuse', 'cgaxis_tree']
saved = []
for img in bpy.data.images:
    if not img.packed_file:
        continue
    if any(k in img.name for k in want):
        ext = 'png' if 'png' in img.name.lower() else 'jpg'
        fn = f"{img.name.replace('#', '').replace('.', '_').strip('_')}.{ext}"
        try:
            data = img.packed_file.data
            with open(os.path.join(OUT, fn), 'wb') as f:
                f.write(bytes(data))
            saved.append((img.name, fn, list(img.size)))
        except Exception as e:
            saved.append((img.name, 'FAIL ' + str(e), []))

mat = bpy.data.materials.get('034- Default.001')
info = {'nodes': [], 'links': []}
for n in mat.node_tree.nodes:
    nd = {'name': n.name, 'type': n.bl_idname, 'inputs': {}}
    for i in n.inputs:
        try:
            v = i.default_value
            nd['inputs'][i.name] = list(v) if hasattr(v, '__len__') else v
        except Exception:
            pass
    if n.bl_idname == 'ShaderNodeTexImage' and n.image:
        nd['image'] = n.image.name
    info['nodes'].append(nd)
for l in mat.node_tree.links:
    info['links'].append([l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name])

with open(r'D:/project/blender_learning/scripts/foliage_mat.json', 'w', encoding='utf-8') as f:
    json.dump({'saved_images': saved, 'material': info}, f, ensure_ascii=False, indent=1)
print('SAVED', saved)
