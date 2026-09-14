import bpy
import colorsys
from collections import defaultdict, deque, Counter

TARGETS = {"外裙子", "鞋子"}
obj = bpy.data.objects.get("鸣潮_今汐_桃夭灼灼1.0311_mesh")
uv_layer = obj.data.uv_layers.active


def sample_image(image, uv):
    width, height = image.size
    x = max(0, min(width - 1, int(uv.x * (width - 1))))
    y = max(0, min(height - 1, int((1.0 - uv.y) * (height - 1))))
    offset = (y * width + x) * 4
    return tuple(float(image.pixels[offset + channel]) for channel in range(3))


for slot_index, slot in enumerate(obj.material_slots):
    material = slot.material
    if not material or material.name not in TARGETS:
        continue
    texture = material.node_tree.nodes.get("mmd_base_tex")
    image = texture.image if texture else None
    polygons = [poly for poly in obj.data.polygons if poly.material_index == slot_index]
    vertex_to_faces = defaultdict(list)
    for local_index, poly in enumerate(polygons):
        for vertex_index in poly.vertices:
            vertex_to_faces[vertex_index].append(local_index)
    seen = set()
    components = []
    for start in range(len(polygons)):
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for vertex_index in polygons[current].vertices:
                for neighbor in vertex_to_faces[vertex_index]:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        queue.append(neighbor)
        points = [obj.data.vertices[index].co for face_index in component for index in polygons[face_index].vertices]
        mins = [min(point[index] for point in points) for index in range(3)]
        maxs = [max(point[index] for point in points) for index in range(3)]
        center = tuple((maxs[index] + mins[index]) * 0.5 for index in range(3))
        if len(component) < 20 or (material.name == "外裙子" and (abs(center[0]) > 0.12 or center[2] < 1.0)):
            continue
        hues = []
        rgbs = []
        step = max(1, len(component) // 80)
        for face_index in component[::step]:
            poly = polygons[face_index]
            uvs = [uv_layer.data[index].uv for index in poly.loop_indices]
            uv = sum(uvs, uvs[0].copy()) / (len(uvs) + 1)
            rgb = sample_image(image, uv)
            rgbs.append(rgb)
            hues.append(colorsys.rgb_to_hsv(*rgb))
        avg = [sum(rgb[channel] for rgb in rgbs) / len(rgbs) for channel in range(3)]
        bins = Counter(int(hsv[0] * 24) % 24 for hsv in hues if hsv[1] > 0.12 and hsv[2] > 0.08)
        print(material.name, "polys", len(component), "center", tuple(round(value, 3) for value in center), "avg_rgb", tuple(round(value, 3) for value in avg), "hues", bins.most_common(5))
