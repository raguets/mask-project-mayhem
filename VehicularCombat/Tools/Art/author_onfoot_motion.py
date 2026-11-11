"""Blender MCP only: author reusable in-place biped actions on the existing four rigs.

Human gait/weapon-ready poses are gameplay interpretations, not official M.A.S.K. motion.
Original blends, geometry, weights, heads and masks are never overwritten.
"""
import bpy, json, math, traceback
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion

ROOT=Path('G:/DEV/mask-project-mayhem/VehicularCombat')
OUT=ROOT/'SourceArt/MASK/OnFoot';OUT.mkdir(parents=True,exist_ok=True)
STATUS=ROOT/'Saved/Art/onfoot';STATUS.mkdir(parents=True,exist_ok=True)
CONTRACT=json.loads((STATUS/'fleet-rigs.json').read_text(encoding='utf-8'))
STATE={'actor':-1,'actions':[],'current':None,'reports':[]}

def mark(stage,**extra):
    (OUT/'progress.json').write_text(json.dumps({'stage':stage,**extra},indent=2),encoding='utf-8')

def select(obs):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.hide_set(False);ob.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]

def world_bone(rig,name,head,direction):
    bone=rig.pose.bones[name];rest=bone.bone.matrix_local.to_quaternion()
    axis=rest@Vector((0,1,0));rotation=axis.rotation_difference(direction.normalized())@rest
    bone.rotation_mode='QUATERNION';bone.matrix=Matrix.Translation(head)@rotation.to_matrix().to_4x4()
    bpy.context.view_layer.update()

def limb(rig,upper,lower,end,target,pole,end_direction):
    a=rig.pose.bones[upper];start=a.head.copy();l1=a.bone.length;l2=rig.pose.bones[lower].bone.length
    vec=target-start;distance=max(abs(l1-l2)+.001,min(vec.length,l1+l2-.001));axis=vec.normalized()
    target=start+axis*distance;along=(l1*l1-l2*l2+distance*distance)/(2*distance)
    sideways=pole-start;sideways-=axis*sideways.dot(axis);sideways.normalize()
    joint=start+axis*along+sideways*math.sqrt(max(0,l1*l1-along*along))
    world_bone(rig,upper,start,joint-start);world_bone(rig,lower,joint,target-joint)
    world_bone(rig,end,target,end_direction)

def pose(rig,base,phase,kind,direction=0):
    for name,matrix in base.items():rig.pose.bones[name].matrix_basis=matrix
    moving=kind in ('Walk','Run');running=kind=='Run';jumping=kind=='Jump'
    cycle=.6 if running else 1.;speed=4. if running else 1.5;stance=.28 if running else .5
    direction_vector=Vector((math.cos(direction),math.sin(direction),0))
    offset=(-.11+.02*math.cos(4*math.pi*phase)) if running else (-.09+.012*math.cos(4*math.pi*phase)) if moving else -.008+.002*math.sin(2*math.pi*phase)
    if jumping:offset=-.10+.045*math.sin(math.pi*phase)
    pelvis=rig.pose.bones['pelvis'];head=pelvis.bone.head_local+Vector((0,0,offset))
    lean=(8 if running else 4)*direction_vector.x if moving else 1
    rotation=Quaternion(Vector((0,1,0)),math.radians(lean))@pelvis.bone.matrix_local.to_quaternion()
    pelvis.matrix=Matrix.Translation(head)@rotation.to_matrix().to_4x4();bpy.context.view_layer.update()
    for side,sign,shift in [('L',1,0),('R',-1,.5)]:
        t=(phase+shift)%1.;foot=rig.data.bones['foot.'+side].head_local.copy();ankle_pitch=0
        if moving:
            half=speed*cycle*stance*.5
            if t<stance:
                u=t/stance;travel=half*(1-2*u)
                ankle_pitch=-10*(1-u/.2) if u<.2 else 12*((u-.8)/.2) if u>.8 else 0
            else:
                u=(t-stance)/(1-stance);smooth=u*u*(3-2*u);travel=half*(2*smooth-1)
                foot.z+=(.24 if running else .12)*math.sin(math.pi*u);ankle_pitch=8*math.sin(math.pi*u)
            foot+=direction_vector*travel
            sine=math.sin(math.radians(ankle_pitch));foot.z+=max(.17*sine,-.08*sine)
        elif jumping:foot.x+=.10*math.sin(math.pi*phase);foot.z+=.24*math.sin(math.pi*phase)
        toe=Quaternion(Vector((0,1,0)),math.radians(ankle_pitch))@Vector((.14,sign*.01,-.055))
        limb(rig,'thigh.'+side,'shin.'+side,'foot.'+side,foot,Vector((1,sign*.11,.5)),toe)
    # Two-bone IK preserves joint lengths. The same hands hold the shared rifle.
    bob=offset*.35
    for side,sign,target in [('R',-1,Vector((.30,-.12,1.30+bob))),('L',1,Vector((.42,-.08,1.30+bob)))]:
        limb(rig,'upper_arm.'+side,'forearm.'+side,'hand.'+side,target,Vector((.05,sign*.55,1.13+bob)),Vector((.025,sign*.005,-.085)))

def init_actor(index):
    data=CONTRACT[index];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'SourceArt/MASK/Editable'/data['file']))
    bpy.app.driver_namespace['_mask_asset_review_active']=True
    scene=bpy.context.scene;rig=bpy.data.objects[data['rig']]
    action=bpy.data.actions.get(data['name']+'_Standing');rig.animation_data.action=action;scene.frame_set(1);bpy.context.view_layer.update()
    base={b.name:b.matrix_basis.copy() for b in rig.evaluated_get(bpy.context.evaluated_depsgraph_get()).pose.bones}
    if rig.animation_data.drivers:raise RuntimeError('Unexpected live rig drivers; inspect before editing')
    rig.animation_data.action=None;rig.data.pose_position='POSE'
    meshes=[bpy.data.objects[name] for name in data['meshes']]
    keep=set(meshes+[rig])
    for ob in list(bpy.data.objects):
        if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
    rig['mask_on']=True;rig['motion_interpretation']='Authored generic human gait, existing 17-bone rig and unchanged meshes/weights.'
    for ob in meshes:
        for prop in ('hide_render','hide_viewport'):
            try:ob.driver_remove(prop)
            except (TypeError,RuntimeError):pass
        ob.hide_viewport=False;ob.hide_render=False;ob.hide_set(False)
        mask='mask' in ob.name.lower() or 'spectrum' in ob.name.lower();hair='hair' in ob.name.lower()
        if mask or hair:
            for prop in ('hide_render','hide_viewport'):
                driver=ob.driver_add(prop).driver;v=driver.variables.new();v.name='m';v.targets[0].id=rig;v.targets[0].data_path='["mask_on"]';driver.expression='not m' if mask else 'm'
    scene.render.fps=30;scene.frame_start=1
    actions=[('Idle',0,61),('Jump',0,25)]
    for kind,count in [('Walk',31),('Run',19)]:
        for angle in range(0,360,45):actions.append((kind,angle,count))
    STATE.update(current={'data':data,'rig':rig,'meshes':meshes,'base':base,'clips':[]},actions=actions)

def make_action(item):
    current=STATE['current'];rig=current['rig'];scene=bpy.context.scene;kind,angle,count=item
    label=kind+(str(angle).zfill(3) if kind in ('Walk','Run') else '')
    action=bpy.data.actions.new(current['data']['name']+'_OnFoot_'+label);rig.animation_data.action=action
    for frame in range(1,count+1):
        scene.frame_set(frame);pose(rig,current['base'],(frame-1)/(count-1),kind,math.radians(angle))
        for bone in rig.pose.bones:
            bone.rotation_mode='QUATERNION'
            for path in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=path,frame=frame,group=bone.name)
    action.use_fake_user=True
    current['clips'].append({'name':label,'action':action.name,'frames':count,'speed':150 if kind=='Walk' else 400 if kind=='Run' else 0,'x':(150 if kind=='Walk' else 400)*math.cos(math.radians(angle)) if kind in ('Walk','Run') else 0,'y':-(150 if kind=='Walk' else 400)*math.sin(math.radians(angle)) if kind in ('Walk','Run') else 0})
    mark('AUTHORING',actor=current['data']['name'],clip=label)

def save_export():
    current=STATE['current'];rig=current['rig'];data=current['data'];scene=bpy.context.scene;folder=OUT/data['name'];folder.mkdir(exist_ok=True)
    rig.animation_data.action=bpy.data.actions[current['clips'][0]['action']];scene.frame_set(1);scene.frame_end=61
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/(data['name']+'_Locomotion.blend')))
    # Match the existing imported skeleton's root names and centimetre export contract.
    cm=rig.copy();cm.data=rig.data.copy();scene.collection.objects.link(cm);cm.animation_data_clear();cm.data.transform(Matrix.Diagonal((100.,100.,100.,1.)));cm.matrix_world=Matrix.Identity(4)
    original_name=rig.name;rig.name=original_name+'_Source';cm.name=original_name if data['name']=='Matt' else original_name+'_CM'
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01
    for clip in current['clips']:
        source=bpy.data.actions[clip['action']];rig.animation_data.action=source
        action=bpy.data.actions.new(data['name']+'_CM_OnFoot_'+clip['name']);cm.animation_data_create();cm.animation_data.action=action
        for frame in range(1,clip['frames']+1):
            scene.frame_set(frame);bpy.context.view_layer.update()
            for bone in cm.pose.bones:
                matrix=rig.pose.bones[bone.name].matrix_basis.copy();matrix.translation*=100;bone.matrix_basis=matrix;bone.rotation_mode='QUATERNION'
                for path in ('location','rotation_quaternion','scale'):bone.keyframe_insert(data_path=path,frame=frame,group=bone.name)
        scene.frame_start=1;scene.frame_end=clip['frames'];scene.frame_set(1);select([cm])
        bpy.ops.export_scene.fbx(filepath=str(folder/(clip['name']+'.fbx')),use_selection=True,object_types={'ARMATURE'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.,bake_anim_force_startend_keying=True)
    report={'name':data['name'],'source':data['file'],'rig':original_name,'meshes':data['meshes'],'one_body':True,'face_retained':True,'clips':current['clips'],'interpretation':'Generic human locomotion authored with analytic two-bone IK; not motion capture or an official cartoon animation.'}
    (folder/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8');STATE['reports'].append(report)

def step():
    try:
        if STATE['current'] is None:
            STATE['actor']+=1
            if STATE['actor']>=len(CONTRACT):
                mark('COMPLETE',actors=[r['name'] for r in STATE['reports']]);bpy.ops.wm.open_mainfile(filepath=str(OUT/'Matt/Matt_Locomotion.blend'));return None
            init_actor(STATE['actor']);return .1
        if STATE['actions']:make_action(STATE['actions'].pop(0));return .02
        save_export();STATE['current']=None;return .1
    except Exception:
        mark('ERROR',error=traceback.format_exc());bpy.app.driver_namespace.pop('_mask_asset_review_active',None);return None

if bpy.app.driver_namespace.get('_mask_asset_review_active'):raise RuntimeError('Another art job is active')
bpy.app.driver_namespace['_mask_asset_review_active']=True
bpy.app.timers.register(step,first_interval=.1,persistent=True);mark('QUEUED');print('ONFOOT_MOTION_QUEUED')
