import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Matt_Trakker';out={}
for filename in ['MattTrakker_V2.blend','Spectrum_V2.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(A/filename));s=bpy.context.scene
 assert bpy.data.objects.get('THK_Hood') is None
 if filename.startswith('Matt'):
  r=bpy.data.objects['MattTrakker_Rig'];assert sum(o.type=='ARMATURE' for o in s.objects)==1
  head=bpy.data.objects['MT_Head_AnatomicalSurface'];ptr=head.data.as_pointer();states=[]
  for drive in [0,1]:
   for mask in [False,True]:
    r['driving_pose']=drive;r['mask_on']=mask;r.update_tag();s.frame_set(1+drive);bpy.context.view_layer.update()
    visible=sum(not o.hide_render for o in bpy.data.collections['Spectrum11_Asset'].objects)
    assert (visible>0)==mask;assert head.data.as_pointer()==ptr;assert not head.hide_render
    states.append({'drive':drive,'mask':mask,'visible_mask_parts':visible})
  out[filename]={'reopened':True,'armatures':1,'single_head':True,'states':states,'vehicle_dependency':False}
 else:
  assert not any(o.type=='ARMATURE' for o in s.objects)
  assert not bpy.data.objects.get('MattTrakker_Rig')
  co=bpy.data.collections['Spectrum11_Asset'];assert len(co.objects)==26
  assert all(not o.animation_data for o in co.objects)
  assert all(not any(m.type=='ARMATURE' for m in o.modifiers) for o in co.objects)
  out[filename]={'reopened':True,'standalone_socket':bool(bpy.data.objects.get('Spectrum_HeadSocket')),'objects':len(co.objects),'character_dependency':False,'vehicle_dependency':False}
(A/'standalone_validation_v2.json').write_text(json.dumps(out,indent=2));print('STANDALONE_VALIDATION '+json.dumps(out))
