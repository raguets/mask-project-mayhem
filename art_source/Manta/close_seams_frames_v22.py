import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'rebuild_bindings_v15.py').read_text().split('# Front tires')[0],'<helpers>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=None
def rearx(x):return -.70+(x+.70)*.90 if x<-.70 else x
def basehood(x,y):
 u=max(0,min(1,(x-.73)/1.62));return .875-.025*u-.305*u*u-.005*u**5-.035*(y/.70)**2
def width(x):
 u=max(0,min(1,(x-.73)/1.62));return .33 if u<.86 else .33+.21*min(1,(u-.86)/.10)
# Inner shoulder edge is flush with the central panel. Curved height increase
# develops only across the fixed fender toward the headlight, never as an open slit.
for sign,l in [(1,'L'),(-1,'R')]:
 bpy.data.objects.remove(bpy.data.objects['MA_FixedHoodShoulder_'+l],do_unlink=True);xs=seq(64,.73,2.35);vv=[];K=26
 for x in xs:
  u=(x-.73)/1.62;inner=width(x)+.0015;ys=seq(23,inner,.67)
  def z(y):
   q=max(0,min(1,(y-inner)/max(.005,.58-inner)));return basehood(x,sign*y)+.115*u*u*sin(pi*q/2)**2
  for y in ys:vv.append((x,sign*y,z(y)))
  vv.extend([(x,sign*.67,z(.67)-.035),(x,sign*inner,z(inner)-.035)])
 ff=[tuple(reversed(range(K))),tuple((len(xs)-1)*K+i for i in range(K))]+[(j*K+i,j*K+(i+1)%K,(j+1)*K+(i+1)%K,(j+1)*K+i) for j in range(len(xs)-1) for i in range(K)]
 o=mesh('MA_FixedHoodShoulder_'+l,vv,ff,purple,root,smooth=True,bevel=.0015)
 def subtract(target,cut,name):
  m=target.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut;bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cut,do_unlink=True)
 subtract(o,box('ThinHeadlightBore',(2.20,sign*.60,.60),(.72,.20,.04),None,0),'OpenHeadlightBore')
 # Small fixed headlight brow joins the frame above the sliding tongue clearance.
 o=box('MA_FixedHeadlightBrow',(2.325,sign*.55,.626),(.050,.105,.012),purple,.003,root)
 subtract(o,box('BrowOpenPort',(2.34,sign*.60,.60),(.10,.20,.040),None,0),'BrowPort')
# Rear root edge remains tucked a few centimetres ahead of the closed body end.
for sign in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(sign)];main=bpy.data.objects['MA_MainWing_'+str(sign)];pts=snap(main);lo=min(p.x for p in pts);hi=max(p.x for p in pts)
 def fit(p):p.x=-2.10+(p.x-lo)*(hi+2.10)/(hi-lo);return p
 for o in list(wing.children):
  if o==main or o.name.startswith(('MA_WingPanelLine','MA_AileronSeam')):localize(o,wing,mapdata(o,snap(o),fit))
# One closed flat ring per pane: no overlapping bar ends or tubular corner tabs.
for o in list(bpy.data.objects):
 if o.name.startswith(('MA_FlatWindshield','MA_FlatHatch','MA_FlatQuarter')):bpy.data.objects.remove(o,do_unlink=True)
def ring(name,points,normal,widths):
 pp=[];ww=[]
 for p,w in zip(points,widths):
  p=Vector(p)
  if not pp or (p-pp[-1]).length>.000001:pp.append(p);ww.append(w)
 if (pp[-1]-pp[0]).length<.000001:pp.pop();ww.pop()
 n=Vector(normal).normalized();vv=[];N=len(pp)
 for i,p in enumerate(pp):
  t=(pp[(i+1)%N]-pp[(i-1)%N]).normalized();d=n.cross(t).normalized()
  vv.extend(tuple(p+d*w+n*h) for h in [-.009,.009] for w in [-ww[i]/2,ww[i]/2])
 ff=[]
 for i in range(N):
  a=i*4;b=((i+1)%N)*4;ff.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 return mesh(name,vv,ff,purple,root,bevel=.006)
def wind(t,q):return (.67-.725*t+.055*(1-q*q)+.006*sin(pi*t),(.75-.15*t)*q,.86+.361*t+.008*(1-q*q)*sin(pi*t))
points=[];widths=[]
for edge,w in [([wind(0,q) for q in seq(40,-1,1)],.10),([wind(t,1) for t in seq(40)],.16),([wind(1,q) for q in seq(40,1,-1)],.14),([wind(t,-1) for t in seq(40,1,0)],.16)]:points+=edge;widths +=[w]*len(edge)
ring('MA_FlatWindshieldFrame',points,(.44,0,.90),widths)
def hatch(t,q):return (rearx(-.76-1.36*t),(.62+.10*t)*q,1.21-.39*t+.040*sin(pi*t)+.025*(1-q*q))
points=[hatch(0,q) for q in seq(40,-1,1)]+[hatch(t,1) for t in seq(40)]+[hatch(1,q) for q in seq(40,1,-1)]+[hatch(t,-1) for t in seq(40,1,0)]
ring('MA_FlatHatchFrame',points,(-.28,0,.96),[.108]*len(points))
for sign in [-1,1]:
 a=Vector((rearx(-.76),sign*.62,1.21));b=Vector((-.70,sign*.84,.84));c=Vector((rearx(-2.12),sign*.72,.82));n=(b-a).cross(c-a).normalized()
 if n.y*sign<0:n=-n
 def tri(u,v):
  aa=1-u-v;p=a*aa+b*v+c*u;ac=aa+u
  if ac>.00001:p.z+=.040*ac*sin(pi*u/ac)
  p.y+=sign*.035*27*aa*v*u;return p
 edges=[([tri(t,0) for t in seq(40)],.144),([tri(1-t,t) for t in seq(40)],.144),([tri(0,1-t) for t in seq(40)],.172)];points=[];widths=[]
 for pp,w in edges:points+=pp;widths +=[w]*len(pp)
 ring('MA_FlatQuarterFrame_'+str(sign),points,n,widths)
root['seam_note']='Closed central/shoulder joint follows same curved upper edge, 1.5mm manufacturing clearance; no open raised inner shoulder slit. Fixed headlight brow remains above moving tongue.'
for o in bpy.data.objects:
 if o.type=='MESH':o.data.update()
 o.update_tag()
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V22_Assembly.blend'),compress=True)
print('V22_CLOSED_JOINTS_CONTINUOUS_FLAT_FRAMES_SAVED')
