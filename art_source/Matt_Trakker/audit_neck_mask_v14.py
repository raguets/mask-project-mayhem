import bpy,json
from datetime import datetime
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem')
if bpy.data.objects.get('MattTrakker_Rig') is None:
    if bpy.data.is_dirty:bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Thunderhawk'/('Session_before_v14_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')),copy=True,compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(P/'art_source/Thunderhawk/Thunderhawk_V13.blend'))
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig']
out={'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'rest_bones':{},'states':[],'objects':{}}
for name in ['chest','neck','head']:
    b=r.data.bones[name];out['rest_bones'][name]={'head':list(b.head_local),'tail':list(b.tail_local),'inherit_scale':b.inherit_scale}
saved=(s.frame_current,r['driving_pose'],r['mask_on'],r.location.copy())
for drive in [0,1]:
    r['driving_pose']=drive;r['mask_on']=True;r.location=(0,.4 if drive else 0,0);r.update_tag();s.frame_set(1+drive);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    row={'drive':drive,'bones':{},'parts':{}}
    for name in ['chest','neck','head']:
        pb=r.pose.bones[name];row['bones'][name]={'head':list(r.matrix_world@pb.head),'tail':list(r.matrix_world@pb.tail),'matrix':[list(v) for v in pb.matrix],'scale':list(pb.scale)}
    for name in ['MT_Head_AnatomicalSurface','MT_ContinuousFlightSuit','Spectrum_SilverHelmetShell','Spectrum_DoubleRedNeckSeal_Lower','Spectrum_NeckSealConnectingBody']:
        ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear()
        row['parts'][name]={'min':[min(v[i] for v in vv) for i in range(3)],'max':[max(v[i] for v in vv) for i in range(3)]}
    out['states'].append(row)
for co in ['MT11_Character','Spectrum11_Asset']:
    for ob in bpy.data.collections[co].objects:
        if ob.type!='MESH':continue
        if ob.name.startswith(('MT_Head','MT_Hair','MT_Eye','MT_Iris','MT_Brow','MT_FabricCollar','Spectrum')):
            out['objects'][ob.name]={'groups':[g.name for g in ob.vertex_groups],'minz':min(v.co.z for v in ob.data.vertices),'maxz':max(v.co.z for v in ob.data.vertices),'modifiers':[m.type for m in ob.modifiers]}
fr,drive,mask,loc=saved;r['driving_pose']=drive;r['mask_on']=mask;r.location=loc;r.update_tag();s.frame_set(fr);bpy.context.view_layer.update()
(P/'docs/qa/neck_mask_before_v14.json').write_text(json.dumps(out,indent=2));print(json.dumps(out['states']))
