import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=Path('G:/DEV/mask-project-mayhem/art_source/Manta');S=bpy.context.scene;R=bpy.data.objects['VanessaWarfield_Rig'];D=json.loads((A/'proportions_v19.json').read_text())
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
def geom(n):
 o=bpy.data.objects[n];dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);m=ev.to_mesh();p=[ev.matrix_world@v.co for v in m.vertices];f=[list(face.vertices) for face in m.polygons];ev.to_mesh_clear();return p,BVHTree.FromPolygons(p,f)
def box(n):
 p,tr=geom(n);return {'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)],'centre':list(sum(p,Vector())/len(p))}
S.frame_set(1);bpy.context.view_layer.update();report={'source':bpy.data.filepath,'checks':{},'road':{},'flight':{}}
C=report['checks']
for sign in [-1,1]:
 for label,x in [('Front',D['front_axle_x']),('Rear',D['rear_axle_x'])]:
  n='MA_'+label+'Wheel_'+str(sign)+'_Tire';b=box(n);report['road'][n]=b;C[n+'_centred']=abs(b['centre'][0]-x)<.0001 and abs(b['centre'][1]-sign*.83)<.0001;C[n+'_round']=abs((b['max'][0]-b['min'][0])-(b['max'][2]-b['min'][2]))<.0001
 blade=box('MA_MainWing_'+str(sign));report['road']['wing_'+str(sign)]=blade
 C['wing_'+str(sign)+'_inside_rear_tire']=max(abs(blade['min'][1]),abs(blade['max'][1]))<=.7201
 C['wing_'+str(sign)+'_clears_front_tire']=blade['max'][0]<D['front_axle_x']-.296-.05
 C['wing_'+str(sign)+'_root_tucked']=blade['min'][0]>-.70+(-2.28+.70)*.9
 # Font sits only a few millimetres above the actual wing surface.
 p,tree=geom('MA_MainWing_'+str(sign));text=bpy.data.objects['MA_WingVENOM_'+str(sign)];gp,_=geom(text.name);miss=0;dist=[]
 for v in gp[::max(1,len(gp)//24)]:
  hit=tree.ray_cast(v+Vector((0,0,.01)),Vector((0,0,-1)),.05)
  if hit[0] is None:miss+=1
  else:dist.append(v.z-hit[0].z)
 C['wing_'+str(sign)+'_logo_on_surface']=miss==0 and bool(dist) and max(dist)<.006;report['road']['logo_'+str(sign)]={'misses':miss,'offsets':dist}
board=box('MA_RearLightPanel');report['road']['board']=board;C['board_not_above_rear_body']=board['max'][2]<=.731
tr=geom('MA_RearLightPanel')[1];occlusion=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith(('MA_Reactor','MA_Nozzle')):
  pp,_=geom(o.name)
  for p in pp[::max(1,len(pp)//16)]:
   h=tr.ray_cast(Vector((-5,p.y,p.z)),Vector((1,0,0)),10);occlusion.append(h[0] is not None and h[0].x<p.x)
C['three_jets_fully_masked_samples']=bool(occlusion) and all(occlusion);report['road']['jet_occlusion_samples']=len(occlusion)
for sign in [-1,1]:
 b=box('MA_RearBoardRigidLeg_'+str(sign));size=[b['max'][i]-b['min'][i] for i in range(3)];C['support_'+str(sign)+'_horizontal_stowed']=size[0]>size[2] and b['max'][2]<board['max'][2];C['support_'+str(sign)+'_thin_left_right']=size[1]<.027
C['left_hand_drive']=R.matrix_world.translation.y>.30
wind=bpy.data.objects['MA_Windshield'];raw=[wind.matrix_world@v.co for v in wind.data.vertices];base=[p for p in raw if abs(p.z-.86)<.00001];top=[p for p in raw if abs(p.z-1.221)<.00001];bw=max(p.y for p in base)-min(p.y for p in base);tw=max(p.y for p in top)-min(p.y for p in top);crown=max(p.x for p in base)-min(p.x for p in base)
C['windshield_tapered']=tw<bw*.85;C['windshield_true_transverse_crown']=crown>.05;report['road']['windshield']={'base_width':bw,'top_width':tw,'crown':crown}
C['flat_body_window_frames']=all(bpy.data.objects[n].type=='MESH' for n in ['MA_FlatWindshieldFrame','MA_FlatHatchFrame','MA_FlatQuarterFrame_1','MA_FlatQuarterFrame_-1'])
C['no_white_front_headlight_covers']=not any(o.name.startswith('MA_Headlamp_') for o in bpy.data.objects);C['no_front_bumper_bars']=not any(n in bpy.data.objects for n in ['MA_FrontBumper','MA_FrontIntake'])
S.frame_set(121);bpy.context.view_layer.update();tip=box('MA_SlidingHoodSkin')['max'][0];muzzles=[]
for sign in [-1,1]:
 gun=bpy.data.objects['MA_HeadlightCannonTravel_'+str(sign)];pp=[p for o in gun.children if o.type=='MESH' for p in geom(o.name)[0]];muzzles.append(max(p.x for p in pp))
report['flight']['hammer_tip_x']=tip;report['flight']['muzzle_x']=muzzles;C['hammer_only_just_beyond_guns']=all(.015<tip-x<.035 for x in muzzles)
board=box('MA_RearLightPanel');jetmax=max(box(o.name)['max'][2] for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('MA_Reactor','MA_Nozzle')));report['flight']['board']=board;report['flight']['board_jet_gap']=board['min'][2]-jetmax;C['board_just_above_jets']=.07<board['min'][2]-jetmax<.14
body=bpy.data.objects['VW_ContinuousBodyAndFace'];identity=body.data.as_pointer();four=[]
for pose in [0.,1.]:
 for mask in [False,True]:
  R['driving_pose']=pose;R['mask_on']=mask;R.update_tag();bpy.context.view_layer.update();four.append({'pose':pose,'mask_on':mask,'same_mesh':identity==body.data.as_pointer()})
C['one_body_face_four_states']=all(x['same_mesh'] for x in four);report['character_states']=four
R['driving_pose']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update();report['passed']=all(C.values());(A/'semantic_qa_v24.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':report['passed'],'failed':[k for k,v in C.items() if not v],'checks':len(C)}))
