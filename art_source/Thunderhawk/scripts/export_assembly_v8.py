"""Sample world-origin mesh deltas for a neutral UE LevelSequence import spike."""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
root=Path(__file__).resolve().parents[1]; s=bpy.context.scene
objects=sorted([o for o in s.objects if o.type=='MESH' and o.name.startswith('THK_')],key=lambda o:o.name)
s.frame_set(1); rest={o.name:o.matrix_world.copy() for o in objects}
S=Matrix.Diagonal((100.,-100.,100.,1.)); Si=S.inverted()
samples={o.name:[] for o in objects}; bounds={}
rest_bounds={}
for fr in range(1,194):
    s.frame_set(fr)
    for ob in objects:
        delta=S@(ob.matrix_world@rest[ob.name].inverted())@Si
        loc,q,sc=delta.decompose()
        samples[ob.name].append({'frame':fr-1,'translation':list(loc),'quaternion_xyzw':[q.x,q.y,q.z,q.w],'scale':list(sc)})
    if fr in (1,97,193):
        verts=[]; dg=bpy.context.evaluated_depsgraph_get()
        for ob in objects:
            e=ob.evaluated_get(dg); me=e.to_mesh()
            local=[S@(e.matrix_world@v.co).to_4d() for v in me.vertices]
            verts.extend(local)
            if fr==1:
                rest_bounds[ob.name]={'min':[min(v[i] for v in local) for i in range(3)],'max':[max(v[i] for v in local) for i in range(3)]}
            e.to_mesh_clear()
        bounds[str(fr)]={'min':[min(v[i] for v in verts) for i in range(3)],'max':[max(v[i] for v in verts) for i in range(3)]}
result=[]
for ob in objects:
    entries=samples[ob.name]
    moving=any(abs(v)>1e-5 for e in entries for v in e['translation']) or any(abs(e['quaternion_xyzw'][3]-1)>1e-5 or any(abs(x-1)>1e-5 for x in e['scale']) for e in entries)
    result.append({'name':ob.name,'animated':moving,'rest_bounds_cm':rest_bounds[ob.name],'samples':entries if moving else entries[:1]})
data={'version':'V8','fps':24,'sequence_frames':[0,192],'axis_conversion':'Blender(X,Y,Z)m -> UE(X,-Y,Z)cm','world_origin_baked_meshes':True,'objects':result,'bounds_cm':bounds}
(root/'exports'/'THK_V8_assembly.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
print('ASSEMBLY_V8',len(result),'objects',sum(x['animated'] for x in result),'animated')
s.frame_set(1)
