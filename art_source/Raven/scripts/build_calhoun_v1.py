"""Distinct editable Calhoun interpretation on a preserved, copied CC0 rig basis."""
import bpy,json,math,random
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
tau=2*pi
C=bpy.data.collections['CB_Character'];R=next(o for o in C.all_objects if o.type=='ARMATURE');R.name='CalhounBurns_Rig';R.data=R.data.copy();R.data.name='CB_EditableSkeleton'
R['driving_pose']=0.;R['gunner_pose']=0.;R['in_vehicle']=0.;R['vehicle_lift']=0.;R['mask_on']=False
for i in range(3):R.driver_remove('location',i)
R.location=(0,0,0);R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
copies={}
for o in list(C.all_objects):
    if o==R:continue
    o.name='CB_'+o.name.removeprefix('HMC_')
    if o.type=='MESH':
        o.data=o.data.copy();o.data.name=o.name+'_Editable'
        for i,m in enumerate(o.data.materials):
            if not m:continue
            if m not in copies:copies[m]=m.copy();copies[m].name='CB_'+m.name.removeprefix('HMC_')
            o.data.materials[i]=copies[m]
    for mod in o.modifiers:
        if mod.type=='ARMATURE':mod.object=R
    if o.animation_data:
        for f in o.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if isinstance(t.id,bpy.types.Object) and t.id.type=='ARMATURE':t.id=R
# Remove the former character's distinctive outfit/groom, not his preserved basis.
for o in list(C.all_objects):
    if any(k in o.name for k in ['BlueChestPanel','ChestIndicator','ChestMedallion','RightHipHolster','CloseCropScalp','ShortCurlGroom']):bpy.data.objects.remove(o,do_unlink=True)
CURRENT=C;PARENT=None;GROUP='calhoun'
NAVY=material('CB_NavyFlightFabric',(.014,.022,.061),0,.69)
ORANGE=material('CB_OrangeArmor',(.72,.12,.014),.12,.35)
CYAN=material('CB_CyanHarness',(.025,.35,.43),.15,.39)
BLACK=material('CB_DarkGloveLeather',(.012,.017,.027),0,.53)
HAIR=material('CB_ChestnutHair',(.072,.023,.012),0,.48)
SKIN=material('CB_Skin_Interpreted',(.50,.28,.17),0,.47)
skinp=next(n for n in SKIN.node_tree.nodes if n.type=='BSDF_PRINCIPLED');skinp.inputs['Subsurface Weight'].default_value=.08
n=SKIN.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=330
b=SKIN.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=.00022
SKIN.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);SKIN.node_tree.links.new(b.outputs['Normal'],skinp.inputs['Normal'])
LIPS=material('CB_LipTint',(.31,.105,.073),0,.48)
for mat in [NAVY,CYAN]:
    ns=mat.node_tree.nodes;ls=mat.node_tree.links;principled=next(n for n in ns if n.type=='BSDF_PRINCIPLED');noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=480;bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.00025;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs['Normal'],principled.inputs['Normal'])
for o in C.all_objects:
    if o.type!='MESH':continue
    if 'Head_Anatomical' in o.name:
        o.data.materials.clear();o.data.materials.append(SKIN);o.data.materials.append(LIPS)
    elif 'GloveSkin' in o.name:
        o.data.materials.clear();o.data.materials.append(BLACK)
        for f in o.data.polygons:f.material_index=0
    elif any(k in o.name for k in ['ContinuousFlightSuit','ArmBand','BootUpper','BootWelt']):
        for i in range(len(o.data.materials)):o.data.materials[i]=NAVY
    elif any(k in o.name for k in ['FittedKneeGuard','FittedYellowBracer','SculptedPauldron','FormedChestYoke','Cuff','OrangeGaiter']):
        for i in range(len(o.data.materials)):o.data.materials[i]=ORANGE
    elif any(k in o.name for k in ['Belt','FabricCollar']):
        for i in range(len(o.data.materials)):o.data.materials[i]=CYAN
    elif 'Brow_' in o.name:
        for i in range(len(o.data.materials)):o.data.materials[i]=HAIR
        for attr in o.data.color_attributes:
            for d in attr.data:d.color=(.072,.023,.012,1)
# Wide squared jaw, strong brow and swept chestnut hair from the illustrated portrait.
for o in C.all_objects:
    if o.type=='MESH' and any(k in o.name for k in ['Head_','Eyeball','Iris_','Brow_']):
        for v in o.data.vertices:
            p=v.co;t=math.exp(-((p.z-1.61)/.07)**2);p.y*=1+.065*t
            if p.x>.02:p.x+=.003*math.exp(-((p.z-1.69)/.045)**2)
        o.data.update()
head=bpy.data.objects['CB_Head_AnatomicalSurface'];suit=bpy.data.objects['CB_ContinuousFlightSuit']
def bind(o,bone='head',weights=None):
    if weights:
        for i,ww in enumerate(weights):
            total=sum(ww.values()) or 1
            for name,w in ww.items():
                group=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);group.add([i],w/total,'REPLACE')
    else:o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
    mod=o.modifiers.new('CalhounEditableSkin','ARMATURE');mod.object=R;mod.use_deform_preserve_volume=True;o.parent=R;return o
def visibility(o,is_mask=False):
    for prop in ['hide_render','hide_viewport']:drive(o,prop,None,'1-m' if is_mask else 'm',[('m',R,'mask_on')])
# Form a scalp on the existing anatomical skull, not a separate head.
vv=[];ff=[];mapping={}
for face in head.data.polygons:
    p=face.center
    if not(p.z>1.727+.018*max(0,p.x/.12) or (p.x<-.015 and p.z>1.68)):continue
    ids=[]
    for k in face.vertices:
        if k not in mapping:
            v=head.data.vertices[k];q=v.co+v.normal*.006
            if q.z>1.73:q.z+=.020*max(0,1-(q.x/.17)**2);q.x-=.010
            mapping[k]=len(vv);vv.append(tuple(q))
        ids.append(mapping[k])
    ff.append(ids)
scalp=bind(mesh('CB_SweptBackScalp',vv,ff,HAIR,smooth=True));visibility(scalp)
tree=BVHTree.FromPolygons([Vector(v) for v in vv],ff)
for j in range(36):
    y=-.105+.210*j/35;points=[]
    for x in seq(18,.105,-.115):
        hit=tree.ray_cast(Vector((x,y,1.95)),Vector((0,0,-1)),.3)
        if hit[0]:points.append(tuple(hit[0]+hit[1]*.002))
    if len(points)>4:
        curve=path('CB_SweptHairStrand_'+str(j),points,.0015,HAIR)
        # Convert in-memory to a weighted editable strand mesh.
        dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(curve.evaluated_get(dg),depsgraph=dg);o=bpy.data.objects.new(curve.name+'_Mesh',me);C.objects.link(o);bpy.data.objects.remove(curve,do_unlink=True);bind(o);visibility(o)
sv=suit.data.vertices;sf=suit.data.polygons;cloth=BVHTree.FromPolygons([v.co for v in sv],[list(f.vertices) for f in sf])
def fitted_strap(name,start,end,width,back=False):
    vv=[];ff=[];ww=[];start,end=Vector(start),Vector(end)
    for i in range(35):
        t=i/34;p=start.lerp(end,t)
        for side in [-1,1]:
            y=p.y+side*width/2;z=p.z;origin=Vector((-.4 if back else .4,y,z));direction=Vector((1 if back else -1,0,0));hit=cloth.ray_cast(origin,direction,.8)
            if not hit[0]:hit=cloth.find_nearest(Vector((p.x,y,z)))
            pos,normal,index,distance=hit;q=pos+normal*.013;vv.append(tuple(q));face=sf[index];nearest=min((sv[k] for k in face.vertices),key=lambda v:(v.co-q).length_squared);ww.append({suit.vertex_groups[g.group].name:g.weight for g in nearest.groups})
    for i in range(34):ff.append((i*2,i*2+1,i*2+3,i*2+2))
    o=bind(mesh(name,vv,ff,CYAN,smooth=True),weights=ww);solid=o.modifiers.new('HarnessThickness','SOLIDIFY');solid.thickness=.004
for sg,label in [(1,'L'),(-1,'R')]:
    fitted_strap('CB_CyanShoulderHarness_'+label,(.12,sg*.17,1.46),(.12,sg*.11,1.325),.05)
    fitted_strap('CB_BackHarness_'+label,(-.12,sg*.17,1.45),(-.10,0,1.20),.04,True)
    fitted_strap('CB_BackHarnessLower_'+label,(-.1,0,1.20),(-.10,sg*.12,1.08),.033,True)
# Broad orange respirator, dark visor and two side housings, as in supplied portrait.
MASK=collection('CB_Mask');CURRENT=MASK;GROUP='mask'
SHELL=material('CB_OrangeMaskShell',(.80,.13,.012),.28,.30)
VISOR=material('CB_SmokeVisor',(.014,.025,.035),.47,.13)
JOINT=material('CB_MaskDarkJoint',(.023,.030,.035),.12,.52)
rows=[(1.545,.105,.106),(1.60,.139,.132),(1.69,.145,.143),(1.76,.132,.133),(1.82,.096,.110),(1.858,.018,.030)]
vv=[];ff=[];N=64
for z,rx,ry in rows:
    for i in range(N):a=i*tau/N;vv.append((-.015+rx*cos(a),ry*sin(a),z))
for j in range(len(rows)-1):
    for i in range(N):
        a=tau*(i+.5)/N
        if j<3 and math.cos(a)>.35:continue
        ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
o=bind(mesh('CB_MaskDomeAndRearShell',vv,ff,SHELL,smooth=True));solid=o.modifiers.new('ShellThickness','SOLIDIFY');solid.thickness=.004
patcho=patch('CB_DarkWrapVisor',seq(32,-1,1),seq(10),lambda u,t:(.136+.025*(1-u*u),.124*u,1.677+.085*t-.018*abs(u)),VISOR,thick=.004,sub=1,orient=(1,0,0));bind(patcho)
poly=[(.171,-.070,1.681),(.171,.070,1.681),(.197,.064,1.620),(.169,.042,1.548),(.169,-.042,1.548),(.197,-.064,1.620)]
o=bind(mesh('CB_TaperedRespirator',poly,[(0,1,2,3,4,5)],SHELL,bevel=.002));mod=o.modifiers.new('RespiratorWall','SOLIDIFY');mod.thickness=.014
for z in [1.568,1.588,1.608,1.628,1.648]:
    center=.175+.022*math.exp(-((z-1.62)/.04)**2);bind(box('CB_RespiratorVent_'+str(z),(center,0,z),(.007,.090,.004),JOINT,.001))
bind(box('CB_RespiratorCenterRib',(.200,0,1.62),(.010,.011,.098),SHELL,.003))
for sg,label in [(1,'L'),(-1,'R')]:
    bind(box('CB_SideFilter_'+label,(-.005,sg*.153,1.699),(.12,.037,.15),SHELL,.014))
    bind(box('CB_SideFilterInset_'+label,(.06,sg*.173,1.699),(.015,.006,.114),JOINT,.003))
    poly=[(.128,sg*.106,1.680),(.169,sg*.070,1.675),(.172,sg*.044,1.548),(.105,sg*.102,1.552)]
    o=bind(mesh('CB_AngularCheek_'+label,poly,[(0,1,2,3)],SHELL,bevel=.003));o.modifiers.new('CheekWall','SOLIDIFY').thickness=.005
    bind(box('CB_CyanNeckSeal_'+label,(-.004,sg*.113,1.544),(.18,.035,.035),CYAN,.010))
# The photographed crown has raised swept channels, not a cylindrical sleeve.
for y in [-.056,0,.056]:
    points=[]
    for x in seq(20,-.10,.094):
        z=1.768+.095*math.sqrt(max(0,1-((x+.01)/.14)**2-(y/.15)**2));points.append((x,y,z+.005))
    curve=path('CB_CrownRidge_'+str(y),points,.007,SHELL)
    dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(curve.evaluated_get(dg),depsgraph=dg);o=bpy.data.objects.new(curve.name+'_Mesh',me);MASK.objects.link(o);bpy.data.objects.remove(curve,do_unlink=True);bind(o)
for o in MASK.all_objects:visibility(o,True)
R['asset_version']='Calhoun Burns V1';R['reference_note']='Realistic anatomy and unshown geometry interpretation explicitly authorized 2026-11-11. Supplied navy/orange/cyan figurine and illustrated portrait, not a scan or likeness of a real person.'
R['anatomy_provenance']='Editable CC0 Blender Human Base Meshes inherited through preserved Hondo source; copied meshes/armature/materials, independently revised face, hair, suit and separate mask.'
R['asset_type']='One character, one head and armature, removable separate mask'
R['driving_pose']=0;R['mask_on']=False;R.update_tag();bpy.context.view_layer.update()
R.location=(-3.4,0,0)
R['in_vehicle']=0.;R['gunner_pose']=0.;R['vehicle_lift']=0.
S.frame_set(1)
bad=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
assert not bad,bad
S['realism_authorization']='User approved realistic Raven/Calhoun unseen anatomy/cockpit interpretation 2026-11-11.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V1_Assembly.blend'),compress=True)
print('CALHOUN_AND_MASK_STUDY_SAVED',len(C.all_objects),len(MASK.all_objects))
