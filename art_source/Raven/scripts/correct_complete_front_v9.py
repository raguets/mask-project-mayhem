"""Latest user correction supersedes the separate-hood interpretation."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V9_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];root['hover_height']=0.;S.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['RV_Body'];PARENT=None;GROUP='front_assembly'
clip=empty('RV_CompleteFront_LongitudinalPivot',(1.32,0,.52),parent=bpy.data.objects['RV_PresentationOffset'])
drive(clip,'rotation_euler',0,'3.141592653589793*min(1,1.5*t)',[('t',root,'transform')])
clip['user_spec']='ENTIRE front unit rolls longitudinally: body/fenders/hood/nose/lamps/front wheels together. Wheels ride up with the inverted front, then fold onto its upper side. No separate lifted hood.'
clip['axis_estimate']='Longitudinal axle height0.52m interpreted; front roll finishes at2/3 of the shared transformation, then wheel secondary fold finishes. Rear/doors continue concurrently.'
def reparent(ob,parent):
    matrix=ob.matrix_world.copy();ob.parent=parent;ob.matrix_parent_inverse=parent.matrix_world.inverted();ob.matrix_world=matrix
hood=bpy.data.objects['RV_Hood_LongitudinalPivot']
hood.driver_remove('rotation_euler',0);hood.driver_remove('location',2);hood.rotation_euler=(0,0,0);hood.location=(1.32,0,.71);bpy.context.view_layer.update();reparent(hood,clip)
hood.name='RV_HoodSkin_FixedInFrontUnit';hood['mechanism_estimate']='Fixed relative to the complete rolling front unit; obsolete separate hood/cam motion removed by user correction.'
for ob in list(bpy.data.objects):
    if ob==clip or ob==hood or ob.parent!=bpy.data.objects['RV_PresentationOffset']:continue
    if any(ob.name.startswith(prefix) for prefix in ['RV_FrontFender_','RV_FrontUpperShoulder_','RV_NoseFascia','RV_FrontDiscLaunchSlot','RV_LowerNoseIntake','RV_FrontDrivingLamp_','RV_SideMarker_','RV_FrontUndertray','RV_HoodBay','RV_DiscLaunch_Control']):reparent(ob,clip)
for sg,side in [(1,'L'),(-1,'R')]:
    # The front wheel carrier is part of the rotating front, not the fixed chassis.
    wheel=bpy.data.objects['RV_FrontWheelFold_'+side]
    wheel.driver_remove('rotation_euler',0);wheel.driver_remove('location',2);wheel.rotation_euler=(0,0,0)
    # Relocate its pivot while preserving every actual wheel/liner/hub mesh at rest.
    children=list(wheel.children);matrices={ob:ob.matrix_world.copy() for ob in children}
    wheel.location=(1.22,sg*.5125,.3775);bpy.context.view_layer.update()
    for ob,matrix in matrices.items():ob.matrix_parent_inverse=wheel.matrix_world.inverted();ob.matrix_world=matrix
    reparent(wheel,clip)
    drive(wheel,'rotation_euler',0,f'{-sg*pi/2}*max(0,3*t-2)',[('t',root,'transform')])
    wheel['user_spec']='Carried by full front roll first; secondary90deg local tilt only, no artificial cam lift. Inverted assembly already puts wheel high.'
    inner=bpy.data.objects['RV_InnerWheelArch_'+side+'_1.22'];reparent(inner,clip)
# Ribbed original underside becomes the visible upper deck after the full inversion.
CURRENT=bpy.data.collections['RV_Body'];PARENT=None;GROUP='front_assembly'
for y in [-.52,-.26,0,.26,.52]:
    box('RV_FrontUndersideRib_'+str(y),(1.29,y,.157),(1.54,.022,.018),bpy.data.materials['RV_BlackRubberTrim'],.004,root=clip)
# Recessed diametric wheel bars hinge45deg out of their rim channels.
CURRENT=bpy.data.collections['RV_RunningGear'];PARENT=None;GROUP='runninggear'
BLACK=bpy.data.materials['RV_BlackRubberTrim'];ALLOY=bpy.data.materials['RV_BrushedAlloy'];DARK=bpy.data.materials['RV_Gunmetal']
for axle,x in [('Front',1.22),('Rear',-1.22)]:
    for sg,side in [(1,'L'),(-1,'R')]:
        fold=bpy.data.objects['RV_'+axle+'WheelFold_'+side]
        old=bpy.data.objects['RV_'+axle+'HubCannonSlide_'+side];old.driver_remove('location',1);old.location.y=sg*1.02;bpy.context.view_layer.update()
        bar=bpy.data.objects['RV_'+axle+'HubCannon_'+side];bore=bpy.data.objects['RV_'+axle+'HubCannonBore_'+side]
        # Restore a true flush slot in the plane of the rim, not a floating bar.
        for v in bar.data.vertices:
            v.co.y=sg*.985+(v.co.y-sg*1.023)*(.020/.042);v.co.z=.335+(v.co.z-.335)*(.045/.075)
        bar.data.update()
        bpy.data.objects.remove(bore,do_unlink=True)
        hinge=empty('RV_'+axle+'RimGunHinge_'+side,(x-.18,sg*.985,.335),parent=fold)
        reparent(bar,hinge);bpy.data.objects.remove(old,do_unlink=True)
        gun='max(0,min(1,(t-.90)/.10))'
        drive(hinge,'rotation_euler',2,f'{sg*pi/4}*{gun}',[('t',root,'transform')])
        drive(hinge,'location',1,f'{sg*.985}+{sg*.018}*{gun}',[('t',root,'transform')])
        hinge['user_spec']='Recessed diametric gun at rest. Raises45deg OUT of rim plane, muzzle toward +X/front. Slight18mm outward deployment, hidden hinge interpreted.'
        tube('RV_'+axle+'HubCannonBore_'+side,(x+.181,sg*.985,.335),(x+.190,sg*.985,.335),.014,DARK,N=24,root=hinge)
        # Two wheel-face segments leave an actual recessed diametric channel.
        for sign in [-1,1]:
            rr=.217;angle=math.asin(.026/rr);start,end=(angle,pi-angle) if sign>0 else (pi+angle,2*pi-angle)
            verts=[(x+rr*cos(a),sg*1.001,.335+rr*sin(a)) for a in seq(64,start,end)]
            face=mesh('RV_'+axle+'RecessedRimFace_'+side+str(sign),verts,[tuple(range(len(verts)))],ALLOY,root=fold)
            face.modifiers.new('WheelFaceWall','SOLIDIFY').thickness=.006
R=bpy.data.objects['CalhounBurns_Rig'];R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=False;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V9_Assembly.blend'),compress=True)
print('RAVEN_COMPLETE_FRONT_AND_RECESSED_GUNS_V9_SAVED')
