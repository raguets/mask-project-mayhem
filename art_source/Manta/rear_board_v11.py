import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1)
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=root
purple=bpy.data.objects['MA_MainBody'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0]
red=bpy.data.materials.get('MA_RedTailLens') or next(m for m in bpy.data.materials if m.name.startswith('MA_RedTailLens'))
amber=next(m for m in bpy.data.materials if m.name.startswith('MA_AmberLamps'));lamp=bpy.data.objects[next(o.name for o in bpy.data.objects if o.name.startswith('MA_Headlamp'))].data.materials[0]
chrome=next(m for m in bpy.data.materials if m.name.startswith('MA_Alloy'))
# Only the light-bearing board becomes the spoiler. Remove the separate cap/spoiler.
old=bpy.data.objects['MA_RearLightSpoilerHinge']
for ob in list(old.children_recursive)+[old]:bpy.data.objects.remove(ob,do_unlink=True)
carriage=empty('MA_RearBoardSlide',parent=root)
drive(carriage,'location',0,'-.16*min(1,t/.18)',[('t',root,'transform')])
board=empty('MA_RearLightSpoilerHinge',(-2.20,0,.665),carriage)
q='min(1,max(0,(t-.18)/.82))';s=q+'**2*(3-2*'+q+')'
drive(board,'location',2,'.665+.42*('+s+')',[('t',root,'transform')])
drive(board,'rotation_euler',1,str(pi/2)+'*('+s+')',[('t',root,'transform')])
box('MA_RearLightPanel',(-2.20,0,.665),(.060,1.55,.31),purple,.016,board)
for sign in [-1,1]:
 box('MA_TailRed',(-2.234,sign*.53,.70),(.012,.32,.105),red,.007,board)
 box('MA_TailAmber',(-2.236,sign*.727,.70),(.013,.065,.105),amber,.005,board)
 box('MA_TailReverse',(-2.237,sign*.33,.70),(.013,.07,.105),lamp,.005,board)
 for zz in [.67,.70,.73]:path('MA_TailLensRibs',[(-2.244,sign*.39,zz),(-2.244,sign*.67,zz)],.002,chrome,board)
 # Two thin nested columns; the entire carriage first moves aft, then the board rises.
 # Hidden nesting is an interpreted mechanism, not claimed as a photographed pivot design.
 box('MA_RearBoardLowerLeg_'+str(sign),(-2.20,sign*.60,.38),(.028,.045,.36),purple,.007,carriage)
 mid=empty('MA_RearBoardMiddleStage_'+str(sign),parent=carriage)
 drive(mid,'location',2,'.21*('+s+')',[('t',root,'transform')])
 box('MA_RearBoardMiddleLeg_'+str(sign),(-2.20,sign*.60,.42),(.024,.036,.36),purple,.006,mid)
 upper=empty('MA_RearBoardUpperStage_'+str(sign),parent=carriage)
 drive(upper,'location',2,'.42*('+s+')',[('t',root,'transform')])
 box('MA_RearBoardUpperLeg_'+str(sign),(-2.20,sign*.60,.485),(.020,.028,.36),purple,.005,upper)
 box('MA_RearBoardGuideRail',(-2.19,sign*.60,.30),(.34,.050,.035),black,.008,root)
board['reference_note']='tp_mask_manta_03.jpg and supplied rear three-quarter show light-bearing board horizontal on two thin supports. Aft slide then vertical rise; telescopic nesting interpreted.'
root['rear_board_note']='No separate spoiler above lamps. Persistent light-bearing panel slides aft 16cm first, rises 42cm and turns into horizontal board on two thin supports; third-stage nesting is interpreted.'
# Retract gun tips behind actual headlamp faces in road mode, retain full extension.
for sign in [-1,1]:
 gun=bpy.data.objects['MA_HeadlightCannonTravel_'+str(sign)]
 for ob in gun.children:
  if ob.type=='MESH':
   for v in ob.data.vertices:v.co.x-=.20
 drive(gun,'location',0,'.08*t+.70*min(1,max(0,(t-.22)/.78))',[('t',root,'transform')])
for ob in bpy.data.objects:
 if ob.name.startswith('MA_Headlamp') and ob.type=='MESH':drive(ob,'location',2,'-.16*min(1,t/.22)',[('t',root,'transform')])
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(61);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V11_Assembly.blend'),compress=True)
print('V11_SAVED')
