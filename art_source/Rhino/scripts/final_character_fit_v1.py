"""Correct remaining visible helmet clearance and garment/face boundaries."""
import bpy,ast,math,json,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert not S.get('final_character_fit_v1')
for name in ['build_rhino_v1.py','build_characters_v1.py']:
 tree=ast.parse((A/'scripts'/name).read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<helpers>','exec'))
for code in ['AS','BS']:
 r=bpy.data.objects['AlexSector_Rig' if code=='AS' else 'BruceSato_Rig'];r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();S.frame_set(1);bpy.context.view_layer.update();CURRENT=bpy.data.collections[code+'_Character'];suit=bpy.data.objects[code+'_ContinuousFlightSuit']
 for f in suit.data.polygons:f.material_index=int(f.center.z<1.08 and abs(f.center.y)<.23)
 # Close the inherited clothing seam over each knee using a surface band, blended across the same bones.
 tree=BVHTree.FromPolygons([v.co for v in suit.data.vertices],[list(f.vertices) for f in suit.data.polygons])
 for sg,sd in [(1,'L'),(-1,'R')]:
  vv=[];ff=[];ww=[];N=64;NR=28
  for j in range(NR):
   z=.48+j*.12/(NR-1);cx=.02*(1-max(0,(.535-z)/.42));center=Vector((cx,sg*.11,z))
   for i in range(N):
    angle=i*2*pi/N;d=Vector((cos(angle),sin(angle),0));hit=tree.ray_cast(center,d,.15)
    radius=(hit[0]-center).length if hit[0] else .066
    radius=max(.060,min(.091,radius))+.0018;p=center+d*radius;vv.append(tuple(p));u=max(0,min(1,(z-.49)/.09));u=u*u*(3-2*u);ww.append({'thigh.'+sd:u,'shin.'+sd:1-u})
  for j in range(NR-1):ff.extend((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for i in range(N))
  bind(mesh(code+'_ContinuousKneeFabric_'+sd,vv,ff,bpy.data.materials[code+'_TrouserFabric'],smooth=True),r,weights=ww)
 if code=='AS':
  for name in ['AS_FittedRedBeard','AS_RedMoustache','AS_BeardShortFibers']:
   ob=bpy.data.objects.get(name)
   if ob:bpy.data.objects.remove(ob,do_unlink=True)
  head=bpy.data.objects['AS_Head_AnatomicalSurface'];verts=[];faces=[];mapping={};density=[]
  def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
  def amount(p):
   upper=1.622+.043*min(1,abs(p.y)/.073);a=smooth((upper-p.z)/.008)*smooth((p.z-1.549)/.009)
   if abs(p.y)<.035 and p.z>1.618:a*=smooth((1.624-p.z)/.006)
   mouth=(p.y/.035)**2+((p.z-1.604)/.012)**2;a*=smooth((mouth-1)/.3)
   moustache=smooth((.045-abs(p.y))/.009)*smooth((p.z-1.614)/.006)*smooth((1.632-p.z)/.006)
   if p.x<.075:moustache=0
   return max(a,moustache)*smooth((p.x-.018)/.014)
  for face in head.data.polygons:
   p=face.center
   if p.x<.012 or not 1.542<p.z<1.68:continue
   faceindices=[]
   for index in face.vertices:
    if index not in mapping:
     v=head.data.vertices[index];mapping[index]=len(verts);verts.append(tuple(v.co+v.normal*.0035));density.append(amount(v.co))
    faceindices.append(mapping[index])
   faces.append(faceindices)
  beard=material('AS_BeardFiberSurface',(.18,.026,.004),0,.93);ns=beard.node_tree.nodes;ls=beard.node_tree.links;p=next(n for n in ns if n.type=='BSDF_PRINCIPLED');attribute=ns.new('ShaderNodeAttribute');attribute.attribute_name='BeardDensity';ls.new(attribute.outputs['Alpha'],p.inputs['Alpha']);noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=450;bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.0005;ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs['Normal'],p.inputs['Normal'])
  ob=mesh('AS_GraduatedBeard',verts,faces,beard,smooth=True);attr=ob.data.color_attributes.new(name='BeardDensity',type='FLOAT_COLOR',domain='POINT')
  for i,d in enumerate(density):attr.data[i].color=(1,1,1,d)
  bind(ob,r)
  # Keep hair strands within the dense region; edges fade into the underlying skin.
  rng=random.Random(18);vv=[];ff=[];hair=bpy.data.materials['AS_RedBeard'];next(n for n in hair.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.15,.023,.004,1)
  for face in head.data.polygons:
   p=face.center
   if amount(p)<.8 or rng.random()>.38:continue
   c=p+face.normal*.004;side=Vector((0,.00017,0));idx=len(vv);vv.extend([tuple(c-side),tuple(c+side),tuple(c+Vector((.0005,0,-rng.uniform(.002,.004))))]);ff.append((idx,idx+1,idx+2))
  bind(mesh('AS_ShortBeardGroom',vv,ff,hair),r)
  # Enclose the actual forehead rather than lowering a too-small dome through it.
  capob=bpy.data.objects['AS_MaskSilverCrown']
  for v in capob.data.vertices:
   v.co.x=-.011+(v.co.x+.011)*1.22;v.co.y*=1.16;v.co.z=1.710+(v.co.z-1.710)*1.25
  visor=bpy.data.objects['AS_MaskCurvedBlueVisor']
  for v in visor.data.vertices:v.co.x=-.009+(v.co.x+.009)*1.24;v.co.y*=1.09
 else:
  capob=bpy.data.objects['BS_MaskOrangeCrown']
  for v in capob.data.vertices:v.co.x=-.012+(v.co.x+.012)*1.22;v.co.y*=1.16;v.co.z=1.713+(v.co.z-1.713)*1.2
  surround=bpy.data.objects['BS_RespiratorFaceSurround']
  for v in surround.data.vertices:
   if v.co.z>1.69:v.co.z+=.035;v.co.x=-.008+(v.co.x+.008)*1.125;v.co.y*=1.045
 r.location=(2,-.6 if code=='AS' else .6,1.37);r['driving_pose']=1;r['mask_on']=False;r.update_tag()
S['final_character_fit_v1']='Forehead/crown/visor clearance, faded short beard boundary, shirt material zones, continuous knee cloth.'
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True);print('RHINO_CHARACTER_CLEARANCE_AND_GARMENTS_SAVED')
