import bpy,ast,math,re
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert not S.get('launcher_shortened_v1')
tree=ast.parse((A/'scripts/build_rhino_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<helpers>','exec'))
ROOT=bpy.data.objects['Rhino_Control'];launch=bpy.data.objects['RH_MissileLauncherLift'];S.frame_set(1);bpy.context.view_layer.update()
for ob in launch.children:
 if ob.type=='MESH':
  for v in ob.data.vertices:v.co.x=.02+.80*(v.co.x-.02)
launch.driver_remove('location',0)
variables=[('v',ROOT,'launcher_up'),('h',ROOT,'rear_open'),('b',ROOT,'battle_mode')]
u='min(max(v,min(1,max(0,(b-0.80)/0.20))),min(1,max(0,(max(h,min(1,max(0,(b-0.42)/0.36)))-0.92)/0.08)))'
drive(launch,'location',0,'0.12-1.30*('+u+')',variables)
# Fill the respirator's eye/nose surround, with the same grey material as the supplied drawings.
CURRENT=bpy.data.collections['BS_Mask'];rig=bpy.data.objects['BruceSato_Rig'];rig['driving_pose']=0;rig.location=(0,0,0);rig['mask_on']=True;rig.update_tag();bpy.context.view_layer.update()
tree=ast.parse((A/'scripts/build_characters_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<character_helpers>','exec'))
verts=[];faces=[];N=48
for z,rx,ry in [(1.57,.136,.105),(1.63,.144,.112),(1.70,.12,.11)]:
 for i in range(N):
  angle=-1.10+2.20*i/(N-1);verts.append((-.008+rx*cos(angle),ry*sin(angle),z))
for j in range(2):faces.extend((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i) for i in range(N-1))
ob=bind(mesh('BS_RespiratorFaceSurround',verts,faces,bpy.data.materials['BS_MaskRespirator'],smooth=True),rig);mod=ob.modifiers.new('FaceplateThickness','SOLIDIFY');mod.thickness=.003;visibility(ob,rig,'1-mask')
rig['driving_pose']=1;rig.location=(2,.6,1.37);rig['mask_on']=False;rig.update_tag()
S['launcher_shortened_v1']='Stowed cassette fits between rear hatch and sloped upper glazing; deployed cassette translates aft under roof.'
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True);print('RHINO_STOWED_LAUNCHER_FIT_SAVED')
