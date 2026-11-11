import bpy,json
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
R=bpy.data.objects['HondoMacLean_Rig'];CURRENT=bpy.data.collections['HU_Interior'];PARENT=bpy.data.objects['HU_UpperChassisLift'];GROUP='interior';BLACK=bpy.data.materials['HU_ChassisGraphite'];CHROME=bpy.data.materials['HU_Chrome'];LEATHER=bpy.data.materials['HU_SeatLeather'];report={}
def bounds(name):
    o=bpy.data.objects[name];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
for frame in [1,151]:
    S.frame_set(frame);bpy.context.view_layer.update();report[frame]={'rig_location':list(R.location),'driving':R['driving_pose'],'gunner':R['gunner_pose'],'lift':R['vehicle_lift'],'parts':{name:bounds(name) for name in ['HMC_Head_AnatomicalSurface','HMC_GloveSkin_L','HMC_GloveSkin_R','HMC_BootUpper_L','HMC_MaskDomedCrown','HMC_FlaredRearHelmetApron']}}
S.frame_set(1);bpy.context.view_layer.update()
handcenters=[]
for side in ['L','R']:
    b=report[1]['parts']['HMC_GloveSkin_'+side];handcenters.append(Vector([(a+c)/2 for a,c in zip(b['min'],b['max'])]))
# Fit the steering wheel to the actual driving grip, rather than a guessed dashboard location.
center=(handcenters[0]+handcenters[1])/2;center.x+=.006;radius=(handcenters[0]-handcenters[1]).length/2+.012
path('HU_SteeringRim',[(center.x,center.y+radius*cos(a),center.z+radius*sin(a)) for a in seq(96,0,2*pi)],.012,LEATHER)
tube('HU_SteeringColumn',(.55,.37,1.045),tuple(center),.024,BLACK)
tube('HU_SteeringHub',tuple(center-Vector((.018,0,0))),tuple(center+Vector((.018,0,0))),.041,CHROME)
for a in [0,2*pi/3,4*pi/3]:path('HU_SteeringSpoke_'+str(a),[(center.x,center.y+.035*cos(a),center.z+.035*sin(a)),(center.x,center.y+(radius-.015)*cos(a),center.z+(radius-.015)*sin(a))],.008,CHROME)
for sg in [-1,1]:box('HU_DriverPedal_'+str(sg),(.34,.37+sg*.10,.48),(.025,.075,.09),BLACK,.009)
report['steering_center']=list(center);report['steering_radius']=radius
(A/'hondo_fit_measurements_v1.json').write_text(json.dumps(report,indent=2));S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V2_Assembly.blend'),compress=True);print('HONDO_INITIAL_FIT',json.dumps(report))
