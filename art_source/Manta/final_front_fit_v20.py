import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'rebuild_bindings_v15.py').read_text().split('# Front tires')[0],'<helpers>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=None
rx=json.loads((A/'proportions_v19.json').read_text())['rear_axle_x'];H0=.73;H1=2.35
def rearx(x):return -.70+(x+.70)*.90 if x<-.70 else x
def basehood(x,y):
 u=max(0,min(1,(x-H0)/(H1-H0)));return .875-.025*u-.305*u*u-.005*u**5-.035*(y/.70)**2
def hoodz(x,y):
 u=max(0,min(1,(x-H0)/(H1-H0)));return basehood(x,y)+.115*u*u
def width(x):
 u=max(0,min(1,(x-H0)/(H1-H0)));return .33 if u<.86 else .33+.21*min(1,(u-.86)/.10)
# Fixed shoulders remain strictly convex, and form the upper headlight housings.
for sign,l in [(1,'L'),(-1,'R')]:
 old=bpy.data.objects['MA_FixedHoodShoulder_'+l];bpy.data.objects.remove(old,do_unlink=True)
 xs=seq(60,H0,H1);vv=[];K=18
 for x in xs:
  u=(x-H0)/(H1-H0);blend=max(0,min(1,(u-.84)/.16));inner=(width(x)+.0015)*(1-blend)+.49*blend;lo,hi=(inner,.67) if sign==1 else (-.67,-inner)
  vv.extend((x,y,hoodz(x,y)) for y in seq(15,lo,hi));vv.extend([(x,hi,hoodz(x,hi)-.035),(x,lo,hoodz(x,lo)-.035)])
 ff=[tuple(reversed(range(K))),tuple((len(xs)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(xs)-1) for i in range(K)]
 mesh('MA_FixedHoodShoulder_'+l,vv,ff,purple,root,smooth=True,bevel=.002)
# Rebuild outer skin with matching convex fender crowns, without moving circular arches.
piece='# New matching clean fenders'+(A/'consolidated_surfaces_v17.py').read_text().split('# New matching clean fenders')[1].split('# Rigid supports')[0]
for x in [-2.28,-2.05,-1.45,-2.40,-1.60]:piece=piece.replace(str(x),str(rearx(x)))
piece=piece.replace('(-1.40,-.70,.43)','(-.80,-.70,.43)')
exec(compile(piece,'<matching_convex_fenders>','exec'))
for sign in [-1,1]:subtract(body,cutbox('RigidArmChannel',(rearx(-2.35),sign*.60-.023,.24),(rearx(-1.55),sign*.60+.023,.84)),'RigidArmClearance')
# Two small thin open rectangles at the front, fixed independently of the slider.
for o in list(bpy.data.objects):
 if o.name.startswith('MA_HeadlightPortRim'):bpy.data.objects.remove(o,do_unlink=True)
for sign,l in [(1,'L'),(-1,'R')]:
 gun=bpy.data.objects['MA_HeadlightCannonTravel_'+str(sign)];parts=list(gun.children);saved={o:snap(o) for o in parts};oldend=max(p.x for o,pp in saved.items() if o.type=='MESH' for p in pp);control(gun,root,(0,0,0),loc_expr={0:'.20*t'})
 for o,pp in saved.items():
  def fit(p):p.x+=2.32-oldend;p.y=sign*.60+(p.y-sign*.53)*.50;p.z=.60+(p.z-.58)*.50;return p
  localize(o,gun,mapdata(o,pp,fit))
 xmin=min(p.x for o in parts if o.type=='MESH' for p in snap(o))-.02
 for target in [body,bpy.data.objects['MA_FixedHoodShoulder_'+l]]:subtract(target,cutbox('FixedThinHeadlightBore',(xmin,sign*.60-.10,.58),(2.56,sign*.60+.10,.62)),'IndependentCannonOpening')
 for zz in [.577,.623]:newbox('MA_HeadlightPortRim',(2.34,sign*.60,zz),(.010,.206,.004),purple,root)
 for yy in [-.102,.102]:newbox('MA_HeadlightPortRim',(2.34,sign*.60+yy,.60),(.010,.004,.044),purple,root)
# Fixed front cheek faces join the curved shoulders without a bumper or black bars.
for o in list(bpy.data.objects):
 if o.name.startswith('MA_FixedFrontCheek'):bpy.data.objects.remove(o,do_unlink=True)
for sign in [-1,1]:
 vv=[];ys=seq(28,.55,.78)
 for y in ys:vv.extend([(2.35,sign*y,.285),(2.35,sign*y,hoodz(2.35,y)-.0015)])
 o=mesh('MA_FixedFrontCheek',vv,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(len(ys)-1)],purple,root,smooth=True,bevel=.003)
 subtract(o,cutbox('CheekAperture',(2.32,sign*.60-.10,.58),(2.38,sign*.60+.10,.62)),'ActualThinRectangularHole')
root['final_front_note']='195mm slider travel: hammer tip2.545m, short fixed-cannon tips2.520m (25mm difference). Two front apertures200x40mm, axesZ.600 atY+/- .600. Shortened cassette base horizontal; missiles elevate30deg separately.'
root['convexity_note']='Central bonnet curvature d2z/du2=-.610-.100u^3; fixed shoulders=-.380-.100u^3. Both strictly convex across full length, mild increase toward final30%.'
for o in bpy.data.objects:
 if o.type=='MESH':o.data.update()
 o.update_tag()
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V20_Assembly.blend'),compress=True)
print('V20_FRONT_TAIL_ALL_REMARKS_SAVED')
