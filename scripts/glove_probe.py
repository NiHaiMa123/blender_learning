import bpy,json,collections
out=[]
for o in bpy.data.objects:
 if o.type=='MESH' and (len(o.data.vertices)==1987 or '手套' in o.name):
  out.append(dict(name=o.name,scene=o.name in bpy.context.scene.objects,visible=o.visible_get(),hide=o.hide_get(),collections=[c.name for c in o.users_collection],mods=[dict(type=m.type,target=getattr(getattr(m,'target',None),'name',None),arm=getattr(getattr(m,'object',None),'name',None),bound=getattr(m,'is_bound',None)) for m in o.modifiers],data=o.data.name,users=o.data.users))
print(json.dumps(out,ensure_ascii=False))
o=bpy.data.objects['右手套']; adj=[[] for v in o.data.vertices]
for e in o.data.edges:
 a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen=set();components=[]
for i in range(len(adj)):
 if i in seen:continue
 stack=[i];seen.add(i);ids=[]
 while stack:
  v=stack.pop();ids.append(v)
  for j in adj[v]:
   if j not in seen:seen.add(j);stack.append(j)
 components.append(ids)
print('COMPONENTS',[(len(ids),min(ids),max(ids)) for ids in sorted(components,key=len,reverse=True)])
print('PARENTS',[(a.name, [list(r) for r in a.matrix_world]) for a in [bpy.data.objects['达妮娅_arm'],bpy.data.objects['达妮娅_红色毛茸袖形态_arm']]])
