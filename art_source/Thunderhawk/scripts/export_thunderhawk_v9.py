"""Export editable articulation FBX and neutral static assembly + pose samples.
Only changes a separate background scene. Does not save over the .blend source.
"""
import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk');S=bpy.context.scene
OUT=ROOT/'exports';OUT.mkdir(exist_ok=True)
objects=sorted([o for o in S.objects if o.type=='MESH' and o.name.startswith('THK_')],key=lambda o:o.name)
S.frame_set(1);rest={o.name:o.matrix_world.copy() for o in objects}
convert=Matrix.Diagonal((100.,-100.,100.,1.));inverse=convert.inverted()
samples={o.name:[] for o in objects};bounds={};rest_bounds={}
for fr in range(1,194):
    S.frame_set(fr)
    for ob in objects:
        delta=convert@(ob.matrix_world@rest[ob.name].inverted())@inverse
        loc,q,sc=delta.decompose()
        samples[ob.name].append({'frame':fr-1,'translation':list(loc),'quaternion_xyzw':[q.x,q.y,q.z,q.w],'scale':list(sc)})
    if fr in (1,97,193):
        vv=[];dg=bpy.context.evaluated_depsgraph_get()
        for ob in objects:
            ev=ob.evaluated_get(dg);me=ev.to_mesh();points=[convert@(ev.matrix_world@v.co).to_4d() for v in me.vertices];vv.extend(points)
            if fr==1:rest_bounds[ob.name]={'min':[min(p[i] for p in points) for i in range(3)],'max':[max(p[i] for p in points) for i in range(3)]}
            ev.to_mesh_clear()
        bounds[str(fr)]={'min':[min(p[i] for p in vv) for i in range(3)],'max':[max(p[i] for p in vv) for i in range(3)]}
items=[]
for ob in objects:
    entries=samples[ob.name]
    moving=any(any(abs(x)>1e-5 for x in e['translation']) or abs(e['quaternion_xyzw'][3]-1)>1e-5 or any(abs(x-1)>1e-5 for x in e['scale']) for e in entries)
    items.append({'name':ob.name,'animated':moving,'rest_bounds_cm':rest_bounds[ob.name],'samples':entries if moving else entries[:1]})
data={'version':'V9','fps':24,'sequence_frames':[0,192],'axis_conversion':'Blender(X,Y,Z)m -> UE(X,-Y,Z)cm',
      'world_origin_baked_meshes':True,'objects':items,'bounds_cm':bounds,'production_skeletal_rig':False}
(OUT/'THK_V9_assembly.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
S.frame_set(1)
for ob in S.objects:ob.select_set(False)
for ob in S.objects:
    if ob.name.startswith(('THK_','SOCKET_')) and ob.type in ('EMPTY','MESH'):ob.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects['THK_Root']
bpy.ops.export_scene.fbx(filepath=str(OUT/'THK_V9_Articulated.fbx'),use_selection=True,object_types={'EMPTY','MESH'},
    axis_forward='-Y',axis_up='Z',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,add_leaf_bones=False)
# Independent lab uses evaluated rest meshes baked at the vehicle origin.
dg=bpy.context.evaluated_depsgraph_get();baked=[]
for ob in objects:
    ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
    me.transform(ob.matrix_world);baked.append((ob,me))
for ob,me in baked:
    ob.parent=None;ob.animation_data_clear();ob.modifiers.clear();ob.data=me;ob.matrix_world=Matrix.Identity(4)
for ob in S.objects:ob.select_set(False)
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(OUT/'THK_V9.fbx'),use_selection=True,object_types={'MESH'},
    axis_forward='-Y',axis_up='Z',bake_anim=False,add_leaf_bones=False)
print('THK9_EXPORT',json.dumps({'meshes':len(items),'animated':sum(i['animated'] for i in items),'static_fbx':str(OUT/'THK_V9.fbx'),'articulated_fbx':str(OUT/'THK_V9_Articulated.fbx')}))
