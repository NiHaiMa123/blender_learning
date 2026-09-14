import bpy, json
out={}
for mn in ["皮肤","纱内侧","纱外侧","前带子两条","裙"]:
    m=bpy.data.materials.get(mn)
    if m is None or not m.use_nodes or not m.node_tree:
        out[mn]="MISSING"; continue
    t=m.node_tree; rec={"nodes":[],"links":[]}
    for n in t.nodes:
        inp={}
        for s in n.inputs:
            if s.is_linked: inp[s.name]="LINKED"
            else:
                try:
                    v=s.default_value
                    if hasattr(v,"__len__") and not isinstance(v,(str,bytes)):
                        inp[s.name]=[round(float(x),4) for x in v] if len(v)<=4 else f"len{len(v)}"
                    elif isinstance(v,float): inp[s.name]=round(v,4)
                    else: inp[s.name]=v
                except Exception: inp[s.name]="?"
        rec["nodes"].append({"name":n.name,"type":n.type,"inputs":inp})
    for l in t.links: rec["links"].append(f"{l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")
    out[mn]=rec
print(json.dumps(out, ensure_ascii=False, indent=2))
