import bpy,json
dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or not ob.name.startswith('THK_'):continue
    ev=ob.evaluated_get(dg);me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices]
    lo=[min(v[i] for v in vv) for i in range(3)];hi=[max(v[i] for v in vv) for i in range(3)]
    if lo[2]<-.002 or hi[2]>1.45 or max(abs(lo[0]),abs(hi[0]))>2.55 or max(abs(lo[1]),abs(hi[1]))>1.1:
        rows.append({'name':ob.name,'min':lo,'max':hi})
    ev.to_mesh_clear()
print(json.dumps(rows))
