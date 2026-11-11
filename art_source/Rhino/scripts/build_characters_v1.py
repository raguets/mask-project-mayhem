"""Alex and Bruce: distinct editable adaptations of the proven weighted base.
Supplied drawings/toys guide likeness; unshown anatomy interpreted, no real likeness.
"""
import bpy,math,json,ast,random
from pathlib import Path
from math import sin,cos,pi,exp
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert Path(bpy.data.filepath).name=='Rhino_V1.blend'
assert not bpy.data.objects.get('AlexSector_Rig')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1_before_characters.blend'),copy=True,compress=True)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
# Reuse geometry functions, without running the vehicle build or its file mutations.
tree=ast.parse((A/'scripts/build_rhino_v1.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[node for node in tree.body if isinstance(node,ast.FunctionDef)],type_ignores=[]),'<rhino_geometry_functions>','exec'))
BLACK=bpy.data.materials.get('Rhino_ChassisGraphite');ALU=bpy.data.materials.get('Rhino_SatinAluminium');CHROME=bpy.data.materials.get('Rhino_Chrome');ORANGE=bpy.data.materials.get('Rhino_OrangeStripe');GOLD=bpy.data.materials.get('Rhino_GoldStripe');DARK=bpy.data.materials.get('Rhino_Recess');LEATHER=bpy.data.materials.get('Rhino_CharcoalUpholstery')
reports=[]
def bind(ob,rig,bone='head',weights=None):
 if weights:
  for i,items in enumerate(weights):
   for name,value in items.items():
    vg=ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name);vg.add([i],value,'REPLACE')
 else:
  vg=ob.vertex_groups.new(name=bone);vg.add(list(range(len(ob.data.vertices))),1,'REPLACE')
 mod=ob.modifiers.new('EditableCharacterSkin','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True;ob.parent=rig;return ob
def skin_shell(name,source,selection,m,offset,rig):
 indices={};verts=[];faces=[];weights=[]
 for face in source.data.polygons:
  if not selection(face):continue
  mapped=[]
  for index in face.vertices:
   if index not in indices:
    v=source.data.vertices[index];indices[index]=len(verts);verts.append(tuple(v.co+v.normal*offset));weights.append({source.vertex_groups[g.group].name:g.weight for g in v.groups})
   mapped.append(indices[index])
  faces.append(mapped)
 ob=mesh(name,verts,faces,m,smooth=True);bind(ob,rig,weights=weights);solid=ob.modifiers.new('GarmentEdgeThickness','SOLIDIFY');solid.thickness=.002;return ob
def visibility(ob,rig,expression):
 for prop in ['hide_render','hide_viewport']:
  f=ob.driver_add(prop);d=f.driver;d.expression=expression;v=d.variables.new();v.name='mask';v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path='["mask_on"]'
def redefine_driving_legs(rig):
 rig['driving_pose']=0;rig.update_tag();S.frame_set(1);bpy.context.view_layer.update();names=['thigh.L','thigh.R','shin.L','shin.R','foot.L','foot.R']
 # Remove only this pose control's leg curves; preserve the repaired neck and hand driver setup.
 for name in names:
  for prop in ['location','rotation_quaternion','scale']:
   try:rig.pose.bones[name].driver_remove(prop)
   except Exception:pass
  pb=rig.pose.bones[name];pb.location=(0,0,0);pb.rotation_mode='QUATERNION';pb.rotation_quaternion=(1,0,0,0);pb.scale=(1,1,1)
 standing={n:(tuple(rig.pose.bones[n].location),tuple(rig.pose.bones[n].rotation_quaternion),tuple(rig.pose.bones[n].scale)) for n in names}
 rig['driving_pose']=1;rig.update_tag();bpy.context.view_layer.update()
 for sg,sd in [(1,'L'),(-1,'R')]:
  targets={'thigh.'+sd:((-.39,sg*.095,.51),(.025,sg*.115,.50)),'shin.'+sd:((.025,sg*.115,.50),(.18,sg*.115,.08)),'foot.'+sd:((.18,sg*.115,.08),(.32,sg*.115,.06))}
  for name,(a,b) in targets.items():
   pb=rig.pose.bones[name];bone=rig.data.bones[name];a,b=Vector(a),Vector(b);q=(bone.tail_local-bone.head_local).rotation_difference(b-a)@bone.matrix_local.to_quaternion();pb.matrix=Matrix.LocRotScale(a,q,Vector((1,(b-a).length/bone.length,1)));bpy.context.view_layer.update()
 driving={n:(tuple(rig.pose.bones[n].location),tuple(rig.pose.bones[n].rotation_quaternion),tuple(rig.pose.bones[n].scale)) for n in names}
 for name in names:
  pb=rig.pose.bones[name]
  for k,prop in enumerate(['location','rotation_quaternion','scale']):
   aa=standing[name][k];bb=list(driving[name][k])
   if prop=='rotation_quaternion' and sum(a*b for a,b in zip(aa,bb))<0:bb=[-q for q in bb]
   for i,(a,b) in enumerate(zip(aa,bb)):
    f=pb.driver_add(prop,i);d=f.driver;d.expression=f'{a:.12g}+p*({b-a:.12g})';v=d.variables.new();v.name='p';v.type='SINGLE_PROP';v.targets[0].id=rig;v.targets[0].data_path='["driving_pose"]'
 rig['driving_pose']=0;rig.update_tag();bpy.context.view_layer.update()
def helmet_loft(name,rows,mat,rig,suit,opening=False):
 verts=[];faces=[];weights=[];N=80
 bv=BVHTree.FromPolygons([v.co for v in suit.data.vertices],[list(f.vertices) for f in suit.data.polygons]);sv=suit.data.vertices
 for j,(z,rx,ry) in enumerate(rows):
  for i in range(N):
   a=2*pi*i/N;p=Vector((-.015+rx*cos(a),ry*sin(a),z));ww={'head':1.}
   if j<2:
    hit=bv.ray_cast(Vector((p.x,p.y,1.62)),Vector((0,0,-1)),.6)
    if hit[0]:
     if j==0:p.z=hit[0].z+.006
     face=suit.data.polygons[hit[2]];v=min((sv[k] for k in face.vertices),key=lambda v:(v.co-hit[0]).length_squared);ww={suit.vertex_groups[g.group].name:g.weight for g in v.groups}
     if j==1:ww={**{k:w*.5 for k,w in ww.items()},'head':.5}
   verts.append(tuple(p));weights.append(ww)
 for j in range(len(rows)-1):
  for i in range(N):
   a=2*pi*(i+.5)/N;z=(rows[j][0]+rows[j+1][0])/2
   if opening and cos(a)>.48 and 1.535<z<1.72:continue
   faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
 ob=mesh(name,verts,faces,mat,smooth=True);bind(ob,rig,weights=weights);mod=ob.modifiers.new('HelmetWall','SOLIDIFY');mod.thickness=.004;return ob
def cap(name,center,radii,m,rig):
 v=[];f=[];N=64;R=18
 for j in range(R):
  theta=.005+(pi*.49)*j/(R-1)
  for i in range(N):
   a=i*2*pi/N;v.append((center[0]+radii[0]*sin(theta)*cos(a),center[1]+radii[1]*sin(theta)*sin(a),center[2]+radii[2]*cos(theta)))
 for j in range(R-1):f.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
 return bind(mesh(name,v,f,m,smooth=True),rig)

for code,rig_name,yy in [('AS','AlexSector_Rig',-.60),('BS','BruceSato_Rig',.60)]:
 with bpy.data.libraries.load(str(P/'art_source/Matt_Trakker/MattTrakker_V5.blend'),link=False) as (src,dst):dst.collections=['MT11_Character']
 char=dst.collections[0];S.collection.children.link(char);char.name=code+'_Character'
 imported=list(char.all_objects);r=next(o for o in imported if o.type=='ARMATURE');r.name=rig_name;r.data.name=code+'_EditableSkeleton';r.location=(0,0,0);r.scale=(1,1,1);r['driving_pose']=0;r['mask_on']=False;r.update_tag();S.frame_set(1);bpy.context.view_layer.update()
 oldnames={o:o.name.split('.')[0] if o.name.endswith('.001') else o.name for o in imported}
 # Separate each person's datablocks and materials from Matt and from the other person.
 mats={}
 for o in imported:
  if o==r:continue
  old=oldnames[o];o.name=code+'_'+old.removeprefix('MT_')
  if o.type=='MESH':
   for i,m in enumerate(o.data.materials):
    if not m:continue
    if m not in mats:mats[m]=m.copy();mats[m].name=code+'_'+m.name
    o.data.materials[i]=mats[m]
  if o.animation_data:
   for f in o.animation_data.drivers:
    for variable in f.driver.variables:
     for target in variable.targets:
      if target.id and target.id.type=='ARMATURE':target.id=r
  for mod in o.modifiers:
   if mod.type=='ARMATURE':mod.object=r
 # Preserve the improved body/head, remove replaced accessories and technical hidden duplicates.
 for o in list(imported):
  if o==r:continue
  old=oldnames[o]
  remove=(any(k in old for k in ['Harness','FrontZip','ZipTooth','CargoPocket','PocketFlap']) or (o.hide_render and not (o.animation_data and o.animation_data.drivers)))
  if code=='AS' and 'Hair_' in old:remove=True
  if remove:bpy.data.objects.remove(o,do_unlink=True)
 CURRENT=char
 suit=next(o for o in char.all_objects if 'ContinuousFlightSuit' in o.name);head=next(o for o in char.all_objects if 'Head_AnatomicalSurface' in o.name)
 r['asset_version']=('Alex Sector' if code=='AS' else 'Bruce Sato')+' V1';r['reference_fidelity']='Interpretation of supplied cartoon portraits and toy photos, no specific real-person likeness.';r['neck_refinement']='Continuous repaired neck retained; reviewed in standing and truck seated pose.'
 r.id_properties_ui('driving_pose').update(min=0,max=1,description='0 debout / 1 assis : meme personnage et memes meshes')
 r.id_properties_ui('mask_on').update(description='Afficher le masque separe ; visage conserve')
 # Distinct facial proportions; lower neck is unchanged to preserve the clean junction.
 def morph(p):
  p=p.copy();t=max(0,min(1,(p.z-1.53)/.075))
  if code=='AS':p.y*=1+.065*t;p.x+=.004*t;p.z+=.006*t
  else:p.y*=1-.035*t;p.x-=.002*t
  return p
 for o in char.all_objects:
  if o.type=='MESH' and any(k in o.name for k in ['Head_','Eyeball','Iris_','Brow_','Hair_']):
   for v in o.data.vertices:v.co=morph(v.co)
   o.data.update()
 for m in mats.values():
  if any(key in m.name for key in ['NaturalBlond','BlondVariation','BrowHair']):
   col=(.012,.009,.007,1) if code=='BS' else (.26,.050,.011,1)
   for n in m.node_tree.nodes if m.use_nodes else []:
    if n.type=='BSDF_PRINCIPLED':n.inputs['Base Color'].default_value=col
    elif n.type=='VALTORGB':
     for e in n.color_ramp.elements:e.color=col
 # Clothing stays a continuous skinned surface; material zones and fitted shells add outfit identity.
 shirt=material(code+'_WovenShirt',(.016,.16,.19) if code=='AS' else (.43,.32,.19),0,.83)
 pants=material(code+'_TrouserFabric',(.15,.065,.028) if code=='AS' else (.43,.32,.19),0,.85)
 vest=material(code+'_Vest',(.39,.45,.44) if code=='AS' else (.022,.031,.040),.05,.58)
 accent=material(code+'_Leather',(.11,.042,.019) if code=='AS' else (.72,.13,.018),0,.49)
 skin=next(m for m in head.data.materials if m)
 suit.data.materials.clear();suit.data.materials.append(shirt);suit.data.materials.append(pants)
 for f in suit.data.polygons:f.material_index=int(f.center.z<1.08)
 for o in char.all_objects:
  if o.type!='MESH':continue
  if any(k in o.name for k in ['ArmBand','Cuff','KneePatch','BootUpper','BootWelt']):
   for i in range(len(o.data.materials)):o.data.materials[i]=accent
  if 'FabricCollar' in o.name:
   for i in range(len(o.data.materials)):o.data.materials[i]=shirt
  if 'GloveSkin' in o.name:
   for i in range(len(o.data.materials)):o.data.materials[i]=skin if code=='AS' else pants
 skin_shell(code+'_FittedVest',suit,lambda f:1.09<f.center.z<1.445 and ((f.center.x<.025) or abs(f.center.y)>.061),vest,.008,r)
 if code=='BS':
  # Chest armor follows the body's front curvature with editable ribs and panel divisions.
  panel=skin_shell('BS_ChestArmorSurface',suit,lambda f:1.12<f.center.z<1.43 and f.center.x>.065 and abs(f.center.y)<.18,vest,.020,r)
  for row in range(2):
   for col in range(5):bind(box('BS_ChestArmorRib_'+str((row,col)),(.144,(col-2)*.053,1.21+row*.11),(.023,.038,.075),vest,.010),r,'chest')
  for sg,sd in [(1,'L'),(-1,'R')]:
   skin_shell('BS_ShoulderArmor_'+sd,suit,lambda f,sg=sg:f.center.y*sg>.13 and f.center.z>1.35,accent,.009,r)
   # Tall orange gaiters retain weighted ankle articulation instead of separate ball joints.
   verts=[];faces=[];weights=[];N=48
   for j in range(18):
    z=.16+j*.31/17;rr=.060+.012*sin(pi*j/17)+.0025*sin(j*2.7)
    for i in range(N):
     a=i*2*pi/N;verts.append((.005+rr*cos(a),sg*.11+rr*sin(a),z));weights.append({'shin.'+sd:1})
   for j in range(17):faces.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
   bind(mesh('BS_OrangeGaiter_'+sd,verts,faces,accent,smooth=True),r,weights=weights)
 else:
  beard=material('AS_RedBeard',(.25,.042,.008),0,.86)
  # A fitted facial surface, retaining the actual jaw shape and lip opening.
  skin_shell('AS_FittedRedBeard',head,lambda f: f.center.x>.020 and 1.553<f.center.z<1.666 and not (abs(f.center.y)<.028 and 1.612<f.center.z<1.638) and (f.center.z<1.637 or abs(f.center.y)>.032),beard,.0025,r)
  skin_shell('AS_RedMoustache',head,lambda f:f.center.x>.095 and abs(f.center.y)<.043 and 1.637<f.center.z<1.655,beard,.0028,r)
  for mat in [beard]:
   ns=mat.node_tree.nodes;ls=mat.node_tree.links;n=ns.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=260;b=ns.new('ShaderNodeBump');b.inputs['Distance'].default_value=.001;b.inputs['Strength'].default_value=.4;ls.new(n.outputs['Fac'],b.inputs['Height']);ls.new(b.outputs['Normal'],next(n for n in ns if n.type=='BSDF_PRINCIPLED').inputs['Normal'])
 # Helmet: independently reusable collection attached to the same head/shoulders.
 mask=collection(code+'_Mask');CURRENT=mask
 if code=='AS':
  navy=material('AS_MaskNavy',(.035,.032,.14),.28,.29);silver=material('AS_MaskPalePanels',(.43,.44,.59),.65,.28);visor=material('AS_MaskBlueVisor',(.018,.19,.43),.60,.14)
  helmet_loft('AS_MaskFlaredHood',[(1.435,.16,.23),(1.49,.151,.21),(1.53,.123,.16),(1.59,.112,.121),(1.68,.111,.113),(1.745,.109,.107)],navy,r,suit,True)
  cap('AS_MaskSilverCrown',(-.011,0,1.735),(.113,.113,.102),silver,r)
  verts=[];faces=[];N=48
  for z in [1.708,1.755]:
   for i in range(N):
    a=-1.22+2.44*i/(N-1);verts.append((-.009+.126*cos(a),.118*sin(a),z+.007*cos(a)))
  faces=[(i,i+1,N+i+1,N+i) for i in range(N-1)];bind(mesh('AS_MaskCurvedBlueVisor',verts,faces,visor,smooth=True),r)
  for sg in [-1,1]:
   ob=box('AS_MaskShoulderPanel_'+str(sg),(.091,sg*.154,1.485),(.025,.075,.055),silver,.008);bind(ob,r,'chest')
  bind(box('AS_MaskFrontPanel',(.150,0,1.47),(.025,.11,.05),silver,.008),r,'chest')
 else:
  silver=material('BS_MaskRespirator',(.40,.46,.49),.60,.3);hood=material('BS_MaskOrange',(.82,.18,.025),.25,.3);lens=material('BS_MaskAmberLenses',(.78,.40,.045),.55,.15)
  helmet_loft('BS_MaskOrangeHood',[(1.48,.125,.15),(1.54,.12,.13),(1.64,.113,.111),(1.735,.107,.105)],hood,r,suit,False)
  cap('BS_MaskOrangeCrown',(-.012,0,1.735),(.111,.109,.105),hood,r)
  helmet_loft('BS_MaskShoulderCollar',[(1.43,.15,.208),(1.465,.147,.193),(1.50,.132,.16),(1.535,.123,.14)],silver,r,suit)
  for sg in [-1,1]:
   bind(tube('BS_GoggleRim_'+str(sg),(.108,sg*.052,1.714),(.142,sg*.052,1.714),.047,silver),r)
   bind(tube('BS_GoggleLens_'+str(sg),(.143,sg*.052,1.714),(.146,sg*.052,1.714),.035,lens),r)
  bind(box('BS_GoggleBridge',(.147,0,1.717),(.020,.026,.019),silver,.006),r)
  bind(tube('BS_RespiratorBody',(.104,0,1.622),(.188,0,1.622),.059,silver,r2=.041),r)
  bind(tube('BS_RespiratorGrille',(.188,0,1.622),(.196,0,1.622),.030,DARK),r)
  for sg in [-1,1]:
   pts=[(.168,sg*.038,1.625),(.179,sg*.065,1.59),(.174,sg*.10,1.53),(.133,sg*.12,1.485)]
   ob=path('BS_BreathingHose_'+str(sg),pts,.016,BLACK)
   # Curve converted for editable head/neck skin binding.
   bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');bind(bpy.context.object,r)
   for j in range(13):
    t=j/12;segment=min(2,int(t*3));u=t*3-segment;a=Vector(pts[segment]).lerp(Vector(pts[segment+1]),u);d=(Vector(pts[segment+1])-Vector(pts[segment])).normalized();ob=tube('BS_HoseRib_'+str((sg,j)),a-d*.003,a+d*.003,.020,ALU,N=16);bind(ob,r)
 for o in mask.all_objects:visibility(o,r,'1-mask');o['reference']='Inspected supplied character drawings/toy photos; unseen helmet surfaces interpreted.'
 for o in char.all_objects:
  if 'Hair_' in o.name:visibility(o,r,'mask')
 redefine_driving_legs(r)
 r.location=(2.0,yy,1.37);r['driving_pose']=1.;r['mask_on']=False;r.update_tag();S.frame_set(1);bpy.context.view_layer.update()
 reports.append({'character':r.name,'one_rig':True,'head':head.name,'head_vertices':len(head.data.vertices),'body':suit.name,'body_vertices':len(suit.data.vertices),'mask_collection':mask.name,'source':'MattTrakker_V5 editable weighted base; independent character-specific meshes/materials/face/garments/mask','seated_location':list(r.location),'interpretation':'Supplied drawn/toy character, generic anatomical interpretation; no real-person likeness.'})
# Driver controls follow the evaluated hands; steering remains on Bruce's side.
CURRENT=bpy.data.collections['Rhino_Interior']
for rig_name,yy in [('BruceSato_Rig',.60),('AlexSector_Rig',-.60)]:
 r=bpy.data.objects[rig_name]
 if rig_name.startswith('Bruce'):
  x=2.162;z=2.16
  path('RH_SteeringRim',[(x,yy+.151*cos(i*2*pi/96),z+.151*sin(i*2*pi/96)) for i in range(97)],.014,LEATHER)
  tube('RH_SteeringColumn',(2.47,yy,2.11),(x,yy,z),.025,BLACK)
  tube('RH_SteeringHub',(x-.018,yy,z),(x+.025,yy,z),.043,BLACK)
  for angle in [0,2*pi/3,4*pi/3]:path('RH_SteeringSpoke_'+str(angle),[(x,yy+.035*cos(angle),z+.035*sin(angle)),(x,yy+.14*cos(angle),z+.14*sin(angle))],.013,ALU)
 else:
  path('RH_CopilotGrabHandle',[(2.19,yy-.19,2.14),(2.16,yy-.19,2.16),(2.16,yy+.19,2.16),(2.19,yy+.19,2.14)],.016,BLACK)
 for sd in ['L','R']:
  ob=next(o for o in bpy.data.collections['BS_Character' if rig_name.startswith('Bruce') else 'AS_Character'].all_objects if 'BootUpper_'+sd in o.name)
  ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();toe=max(p.x for p in pts);zone=[p for p in pts if p.x>toe-.008];target=Vector((toe+.010,sum(p.y for p in zone)/len(zone),sum(p.z for p in zone)/len(zone)))
  box('RH_Pedal_'+rig_name+'_'+sd,target,(.018,.085,.105),BLACK,.01);tube('RH_PedalStem_'+rig_name+'_'+sd,tuple(target+Vector((.15,0,.10))),tuple(target),.012,ALU)
S['characters']='Distinct Alex Sector and Bruce Sato, one rig/head/body per person; visibility controls for separate masks. Generic human interpretation of supplied art.'
(A/'character_build_v1.json').write_text(json.dumps(reports,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True)
print('RHINO_TWO_DISTINCT_CHARACTERS_SAVED',json.dumps(reports))
