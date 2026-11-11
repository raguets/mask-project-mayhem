"""Geometric clearance review, separate from driver timing. Sampled, not continuous."""
import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene;R=bpy.data.objects['HondoMacLean_Rig'];ROOT=bpy.data.objects['Hurricane_Control'];LIFT=bpy.data.objects['HU_UpperChassisLift']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
saved={'frame':S.frame_current,'mask':R['mask_on'],'in_vehicle':R['in_vehicle'],'driving':R['driving_pose']}
def combined(objects,space=None):
    dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];names=[]
    for o in objects:
        if o.type not in {'MESH','CURVE','FONT'}:continue
        e=o.evaluated_get(dg);me=e.to_mesh()
        if not me:continue
        m=e.matrix_world if space is None else space@e.matrix_world;off=len(vs);vs.extend(m@v.co for v in me.vertices);fs.extend(tuple(off+i for i in f.vertices) for f in me.polygons);names.extend([o.name]*len(me.polygons));e.to_mesh_clear()
    return BVHTree.FromPolygons(vs,fs,epsilon=.0003),vs,fs,names
def contacts(a,b):return sorted({(a[3][i],b[3][j]) for i,j in a[0].overlap(b[0])}) if a[1] and b[1] else []
def group(*names):return [o for o in S.objects if o.get('HU_group') in names and not o.name.startswith(('HU_RoofHingePin','HU_SpareSocket'))]
def point_distance(name,target):
    a=combined([bpy.data.objects[name]]);b=combined([bpy.data.objects[target]]);return min(b[0].find_nearest(p)[3] for p in a[1])
report={'method':'Evaluated meshes and curves; surface intersections at every fourth integer frame through 1..241, plus closest hand/control and foot/pedal distances. Intended hinge attachments and stowed housing joins reviewed separately; does not prove continuous absence of collisions or physical steering/cloth simulation.','samples':[],'fit':{},'identities':{},'invalid_drivers':[]}
try:
    R['mask_on']=True;R['in_vehicle']=1.;R['driving_pose']=1.;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
    # Cache the rigid body surfaces in body-local space; all tested mechanisms move relative to it.
    bodyobjs=group('body','glass');body=combined(bodyobjs,LIFT.matrix_world.inverted())
    # Interior static solids are separate so intentional seat/hand contact isn't confused with shell clearance.
    identities={name:(bpy.data.objects[name].as_pointer(),bpy.data.objects[name].data.as_pointer()) for name in ['HondoMacLean_Rig','HMC_Head_AnatomicalSurface','HMC_ContinuousFlightSuit']}
    tireids={o.name:o.data.as_pointer() for o in S.objects if o.name.endswith('_Tire') and o.name.startswith('HU_')}
    for frame in sorted(set(list(range(1,242,4))+[31,55,80,100,120,151,171,191,211,241])):
        S.frame_set(frame);bpy.context.view_layer.update();space=LIFT.matrix_world.inverted();item={'frame':frame,'mode':ROOT['battle_mode'],'pairs':{}}
        for name,objects in [('roof',group('roof','roof_gun','roof_door')),('windshield',group('windshield_hatch','windshield_gun')),('lamps',group('lamp_lens','headlight_gun')),('lower_guns',group('lower_guns')),('saw',group('rear_disc')),('spare',group('spare'))]:
            c=contacts(body,combined(objects,space));
            if c:item['pairs'][name]=c
        c=contacts(combined(group('roof','roof_door'),space),combined(group('roof_gun'),space))
        if c:item['pairs']['roof_weapon_path']=c
        actor=[o for o in S.objects if (o.name.startswith(('HMC_Head_','HMC_Hair','HMC_CloseCrop','HMC_ShortCurl')) or o.name in bpy.data.collections['HMC_Mask'].objects) and not o.hide_render]
        ext=combined(group('roof','roof_door'),space);head=combined(actor,space);c=contacts(body,head)+contacts(ext,head)
        if c:item['pairs']['head_mask']=sorted(set(c))
        # Persistent wheels against outer shell; containing mechanical pockets are checked from geometry and views.
        c=contacts(body,combined([o for o in S.objects if o.name in tireids],space))
        if c:item['pairs']['tires']=c
        assert all(bpy.data.objects[n].data.as_pointer()==i for n,i in tireids.items())
        assert all((bpy.data.objects[n].as_pointer(),bpy.data.objects[n].data.as_pointer())==i for n,i in identities.items())
        if item['pairs']:report['samples'].append(item)
    report['sample_count']=len(sorted(set(list(range(1,242,4))+[31,55,80,100,120,151,171,191,211,241])))
    for frame in [1,151]:
        S.frame_set(frame);bpy.context.view_layer.update();result={}
        for side,sg in [('L',1),('R',-1)]:
            result['hand_'+side+'_m']=point_distance('HMC_GloveSkin_'+side,'HU_SteeringRim' if frame==1 else 'HU_RoofGunGrip_'+str(sg))
            if frame==1:result['pedal_'+side+'_m']=point_distance('HMC_BootUpper_'+side,'HU_DriverPedal_'+str(sg))
            else:
                sole=bpy.data.objects['HMC_BootSole_'+side];e=sole.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();bottom=min((e.matrix_world@v.co).z for v in me.vertices);e.to_mesh_clear();platform=combined([bpy.data.objects['HU_GunnerPlatformTop']]);top=max(p.z for p in platform[1]);result['foot_platform_'+side+'_gap_m']=bottom-top
        report['fit'][str(frame)]=result
    report['identities']={'same_body_head_rig_all_samples':True,'persistent_road_tires':len(tireids),'tires':list(tireids)}
    report['invalid_drivers']=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
    (A/'motion_validation_v4.json').write_text(json.dumps(report,indent=2));print('MOTION_QA',len(report['samples']),'of',report['sample_count'],'frames flagged','FIT',report['fit'],'BAD',report['invalid_drivers'])
finally:
    R['mask_on']=saved['mask'];R['in_vehicle']=saved['in_vehicle'];R['driving_pose']=saved['driving'];R.update_tag();S.frame_set(saved['frame']);bpy.context.view_layer.update()
