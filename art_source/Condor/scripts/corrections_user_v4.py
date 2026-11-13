import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Condor_Control'];R=bpy.data.objects['BradTurner_Rig'];CURRENT=bpy.data.collections['Condor_Vehicle'];PARENT=root
green=bpy.data.materials['Condor_LimePaint'];black=bpy.data.materials['Condor_Charcoal']
for o in list(CURRENT.all_objects):
 if o.name.startswith(('Condor_RearCowl','Condor_Fairing_','Condor_Headlight','Condor_BlackSideInset','Condor_TailVent','Condor_TailRoundVent','Condor_TailGraphic','Condor_Brand')):bpy.data.objects.remove(o,do_unlink=True)
# One watertight chamfered rear block: broad planar sides and top, taper aft.
sections=[(-1.94,.135,.56,.77),(-1.82,.205,.48,.83),(-1.30,.245,.45,.87),(-.64,.265,.43,.88),(-.40,.245,.48,.83)]
vv=[];ff=[]
for x,w,lo,hi in sections:
 ch=.035
 for y,z in [(-w+ch,hi),(w-ch,hi),(w,hi-ch),(w,lo+ch),(w-ch,lo),(-w+ch,lo),(-w,lo+ch),(-w,hi-ch)]:vv.append((x,y,z))
for j in range(len(sections)-1):
 for i in range(8):ff.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
ff.extend([tuple(reversed(range(8))),tuple((len(sections)-1)*8+i for i in range(8))]);mesh('Condor_RearMonobloc',vv,ff,green,bevel=.012)
for side in [-1,1]:
 for x in [-.70,-.91,-1.12]:
  for z in [.64,.74]:box('Condor_RearBlockVent',(x,side*.266,z),(.145,.008,.038),black,.005)
 path('Condor_RearBlockStripe',[(-1.84,side*.208,.54),(-1.30,side*.250,.51),(-.44,side*.249,.54)],.007,black)
# The rotor blades remain fully persistent; rest folds run along the rising side arms.
for side in [-1,1]:
 h=bpy.data.objects['Condor_BladeHinge_'+str(side)];h.location.y=side*.315
 h.animation_data.drivers[0].driver.expression=str(-side)+'*1.570796*(1-max(0,(t-0.72)/0.28))'
# Angular front fairing, planar shoulder/chamfer faces rather than inflated loft.
vv=[];ff=[];front_sections=[(1.42,.185,.73,.94),(1.22,.30,.70,1.00),(.82,.365,.65,1.055),(.49,.31,.65,.99)]
for x,w,lo,hi in front_sections:
 for y,z in [(-w*.72,hi),(w*.72,hi),(w,hi-.07),(w,lo+.03),(w*.45,lo),(-w*.45,lo),(-w,lo+.03),(-w,hi-.07)]:vv.append((x,y,z))
for j in range(3):
 for i in range(8):ff.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
# Square front weapon port, no light lenses. Eight-point inner loop has straight sides.
inn=[(-.072,.895),(.072,.895),(.079,.888),(.079,.744),(.072,.737),(-.072,.737),(-.079,.744),(-.079,.888)]
for y,z in inn:vv.append((1.425,y,z))
for i in range(8):ff.append((i,(i+1)%8,32+(i+1)%8,32+i))
o=mesh('Condor_AngularFrontCowl',vv,ff,green,bevel=.009);o.modifiers.new('FairingWall','SOLIDIFY').thickness=.012
# Deep square socket with dark back; rest cannon is recessed.
for y,z in inn:vv.append((1.27,y,z))
socket_v=[(x,y,z) for x in [1.424,1.27] for y,z in inn];socket_f=[(i,(i+1)%8,8+(i+1)%8,8+i) for i in range(8)];socket_f.append(tuple(range(8,16)));mesh('Condor_SquareWeaponSocket',socket_v,socket_f,black)
gun=bpy.data.objects['Condor_HeadlampCannon']
for o in gun.children:
 if o.type=='MESH':
  for v in o.data.vertices:v.co.z+=.026
for side in [-1,1]:
 poly=[(1.27,side*.277,.80),(1.04,side*.344,.86),(.55,side*.327,.82),(.59,side*.328,.73),(1.15,side*.31,.75)]
 mesh('Condor_AngularBlackInset_'+str(side),poly,[tuple(range(5))],black,bevel=.006)
# Continuous opaque visor seals the eye opening and wraps into the side shell.
CURRENT=bpy.data.collections['BT_Mask'];PARENT=None
old=bpy.data.objects['BT_Hocus_Goggles'];bpy.data.objects.remove(old,do_unlink=True)
dark=bpy.data.materials['BT_HocusPocusVisor'];shell=bpy.data.materials['BT_HocusPocusYellow']
def bind(o):
 o.parent=R;o.vertex_groups.new(name='head').add(list(range(len(o.data.vertices))),1,'REPLACE');o.modifiers.new('EditableMaskSkin','ARMATURE').object=R
 for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
 return o
bind(patch('BT_Hocus_SealedWrapVisor',seq(40,-1,1),seq(16),lambda u,t:(.015+.166*cos(u*1.48),.145*sin(u*1.48),1.668+.143*t-.009*abs(u)),dark,thick=.007,sub=1))
# Solid brow cap joins visor to yellow crown without an eye-level opening.
bind(patch('BT_Hocus_BrowClosure',seq(32,-1,1),seq(6),lambda u,t:(.015+(.166-.056*t)*cos(u*1.48),(.145-.020*t)*sin(u*1.48),1.807+.025*t-.009*abs(u)),shell,thick=.005,sub=1))
root['user_corrections']='2026-11-12: one planar rear block, blades folded alongside pivot arms, single square cannon opening, angular front cowl.'
R['mask_note']='Opaque black visor integral to mask; preserved face underneath.'
bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V4_Assembly.blend'),compress=True)
print('USER_CORRECTIONS_V4_SAVED')
