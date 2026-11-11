"""User corrections: short vertically sliding rear, curved doors, diametric guns."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V4_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
root=bpy.data.objects['Raven_Control'];S.frame_set(1);root['hover_height']=0
cover=bpy.data.objects['RV_ReactorCover_Hinge']
cover.driver_remove('rotation_euler',1);cover.rotation_euler=(0,0,0)
drive(cover,'location',2,'.81+.32*t',[('t',root,'transform')])
cover.name='RV_ReactorCover_VerticalSlide'
cover['user_spec']='Short rear section translates vertically by an estimated0.32m; never hinges or tilts. Four fixed rear lamps remain separate.'
for o in list(cover.children):
    if o.type!='MESH':continue
    for v in o.data.vertices:v.co.x=-2.07+(v.co.x+2.02)*(.32/.59)
    if o.name=='RV_ReactorCover_RearSkirt':
        mean=sum(v.co.x for v in o.data.vertices)/len(o.data.vertices)
        for v in o.data.vertices:v.co.x+=-2.238-mean
    o.data.update()
for sg,side in [(1,'L'),(-1,'R')]:
    for label,start,height,offset in [('Panel',.35,.39,0),('InnerSkin',.36,.36,-.032)]:
        o=bpy.data.objects['RV_DoorWing_'+label+'_'+side]
        for v in o.data.vertices:
            t=max(0,min(1,(v.co.z-start)/height));u=max(0,min(1,(v.co.x+.66)/1.1))
            bow=.082*sin(pi*t)*sin(pi*(.12+.76*u));v.co.y=sg*(.87-.055*t+bow+offset)
            v.co.z+=.012*sin(pi*u)*sin(pi*t)
        o.data.update();o['user_spec']='Convex sculpted Corvette door skin; curved closed and as wing, not a flat board.'
    glass=bpy.data.objects['RV_DoorWing_Glass_'+side]
    for v in glass.data.vertices:
        t=max(0,min(1,(v.co.z-.752)/.37));u=max(0,min(1,(v.co.x+.64)/1.05));v.co.y+=sg*.020*sin(pi*u)*sin(pi*t)
    glass.data.update()
    for axle,x in [('Front',1.22),('Rear',-1.22)]:
        slide=bpy.data.objects['RV_'+axle+'HubCannonSlide_'+side]
        drive(slide,'location',1,f'{sg*1.02}+{sg*.028}*t',[('t',root,'transform')])
        bar=bpy.data.objects['RV_'+axle+'HubCannon_'+side]
        for v in bar.data.vertices:
            v.co.x=x+(v.co.x-x)*(.36/.09);v.co.y=sg*1.023+(v.co.y-sg*1.04)*(.042/.085)
        bar.data.update();bar['user_spec']='Diametric cannon bar lies in rim plane; slight axle-normal deployment only. Bore points along bar, not along axle.'
        old=bpy.data.objects['RV_'+axle+'HubCannonBore_'+side];bpy.data.objects.remove(old,do_unlink=True)
        CURRENT=bpy.data.collections['RV_RunningGear'];PARENT=None;GROUP='runninggear'
        tube('RV_'+axle+'HubCannonBore_'+side,(x+.181,sg*1.023,.335),(x+.190,sg*1.023,.335),.018,bpy.data.materials['RV_Gunmetal'],N=24,root=slide)
# Place the rear floor above the entire folding tire envelope.
tray=bpy.data.objects['RV_RearUndertray']
for v in tray.data.vertices:v.co.z=.72+(v.co.z-.305)*(.03/.075)
tray.data.update()
# Hood clearance lift remains simultaneous; use a higher late-phase cam arc.
hood=bpy.data.objects['RV_Hood_LongitudinalPivot']
drive(hood,'location',2,'.71+1.00*sin(3.141592653589793*t)',[('t',root,'transform')])
hood['mechanism_estimate']='Temporary1.00m peak cam lift for swept clearance while rotating longitudinally. Hidden mounting interpreted; not reference-validated and may be refined.'
S.frame_set(1);R=bpy.data.objects['CalhounBurns_Rig'];R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();bpy.context.view_layer.update()
S['user_corrections_20261111']='Short vertically translating rear cover; convex doors/wings; four diametric rim-plane cannon bars.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V4_Assembly.blend'),compress=True)
print('USER_CORRECTIONS_V4_SAVED')
