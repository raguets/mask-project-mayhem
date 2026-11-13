import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Condor_Control'];R=bpy.data.objects['BradTurner_Rig'];CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=root;s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
# Slim front tip, preserve exact square weapon aperture.
cowl=bpy.data.objects['Condor_AngularFrontCowl']
for v in cowl.data.vertices:
 if v.index<8:v.co.y*=.76
 elif 8<=v.index<16:v.co.y*=.90
 if v.co.x>1.40:v.co.x+=.07
for o in CURRENT.all_objects:
 if o.name.startswith('Condor_SquareWeaponSocket'):
  for v in o.data.vertices:
   if v.co.x>1.40:v.co.x+=.07
# Rear wheel rests 30cm further forward; pivot explicitly fixed to upper rear cowl.
rear=bpy.data.objects['Condor_RearWheelPivot'];rear.location.x+=.15;rear.location.z+=.16
spin=bpy.data.objects['Condor_TailRotorSpin'];spin.location.x+=.15;spin.location.z-=.16
for o in list(CURRENT.all_objects):
 if o.name.startswith('Condor_RearSwingArm'):bpy.data.objects.remove(o,do_unlink=True)
black=bpy.data.materials['Condor_Charcoal'];chrome=bpy.data.materials['Condor_WheelAlloy']
for side in [-1,1]:
 tube('Condor_ConnectedRearFork_'+str(side),(-1.75,side*.11,.80),(-1.55,side*.11,.355),.033,black,root=rear)
 tube('Condor_FixedRearPivot_'+str(side),(-1.75,side*.08,.80),(-1.75,side*.14,.80),.046,chrome)
cut=bpy.data.objects['Condor_RearWheelWell_Cutter']
for v in cut.data.vertices:v.co.x+=.30
root['rear_linkage_note']='Fixed anchor (-1.75,0,0.80), continuous fork follows wheel carrier; rest wheel (-1.55,0,0.355). Dimensions estimated.'
# Compact sealed Hocus Pocus face shell, no ladder-like open mouth cage.
CURRENT=bpy.data.collections['BT_Mask'];PARENT=None
for o in list(CURRENT.all_objects):
 if any(k in o.name for k in ['LowerFrame','UpperFrame','Respirator','BreathingPort','FlaredCheek']):bpy.data.objects.remove(o,do_unlink=True)
shell=bpy.data.materials['BT_HocusPocusYellow'];dark=bpy.data.materials['BT_HocusPocusVisor']
def bind(o):
 o.parent=R;o.vertex_groups.new(name='head').add(list(range(len(o.data.vertices))),1,'REPLACE');o.modifiers.new('EditableMaskSkin','ARMATURE').object=R
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
 return o
rows=[(1.535,.106,.101),(1.565,.126,.108),(1.605,.140,.116),(1.642,.163,.122),(1.680,.153,.132),(1.694,.148,.134)]
vv=[];ff=[];N=49
for z,rx,ry in rows:
 for j in range(N):
  a=-1.40+2.80*j/(N-1);vv.append((.005+rx*cos(a),ry*sin(a),z))
for i in range(len(rows)-1):
 for j in range(N-1):ff.append((i*N+j,(i+1)*N+j,(i+1)*N+j+1,i*N+j+1))
o=bind(mesh('BT_Hocus_FittedClosedFace',vv,ff,shell,smooth=True));o.modifiers.new('SealedFaceWall','SOLIDIFY').thickness=.006
for y in [-.030,0,.030]:bind(tube('BT_Hocus_FlushVent',(.151,y,1.618),(.155,y,1.618),.006,dark,N=16))
bind(box('BT_Hocus_MouthVent',(.137,0,1.575),(.008,.049,.012),dark,.004))
for o in CURRENT.all_objects:
 if o.name.startswith('BT_Hocus_EarInset') and o.type=='MESH':
  for v in o.data.vertices:v.co.y*=.94
# Restore high black boots without changing same weighted body.
for o in bpy.data.collections['BT_Character'].all_objects:
 if 'OrangeGaiter' in o.name:
  for i in range(len(o.data.materials)):o.data.materials[i]=bpy.data.materials['BT_BlackLeather']
suit=bpy.data.objects['BT_ContinuousFlightSuit']
for f in suit.data.polygons:
 if .41<f.center.z<.46:f.material_index=0
R['mask_note']='User 2026-11-12: entire face covered; compact fitted closed mouth/chin shell under opaque integral visor. Face retained underneath.'
R['mask_on']=True;R.update_tag();s.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V8_Assembly.blend'),compress=True)
print('USER_CORRECTIONS_V8_SAVED')
