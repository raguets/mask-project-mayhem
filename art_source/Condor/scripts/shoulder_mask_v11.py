import bpy,math,gc,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Condor'
lock=bpy.app.driver_namespace.get('_mask_asset_review_active')
if lock:
 assert Path(lock['output_dir']).resolve()==(A/'renders/v10_review').resolve()
 fs=[f for f in gc.get_objects() if isinstance(f,types.FunctionType) and f.__name__=='step' and f.__globals__.get('lock_token')==lock['token']];assert len(fs)==1;fn=fs[0]
 if bpy.app.timers.is_registered(fn):bpy.app.timers.unregister(fn)
 fn.__globals__['restore']();(A/'renders/v10_review/CANCELLED').write_text('Stopped for fitted shoulder collar correction.')
R=bpy.data.objects['BradTurner_Rig'];o=bpy.data.objects['BT_HocusPocus_OnePiece'];suit=bpy.data.objects['BT_ContinuousFlightSuit'];R['driving_pose']=0.;R.update_tag();bpy.context.view_layer.update()
sv=suit.data.vertices;sf=suit.data.polygons;tree=BVHTree.FromPolygons([v.co for v in sv],[list(f.vertices) for f in sf]);N=128
vv=[tuple(v.co) for v in o.data.vertices];ff=[tuple(f.vertices) for f in o.data.polygons];mi=[f.material_index for f in o.data.polygons];base=len(vv);weights=[];lower=[]
for i in range(N):
 a=2*math.pi*i/N;x=-.01+.135*math.cos(a);y=.233*math.sin(a);hit=tree.ray_cast(Vector((x,y,1.64)),Vector((0,0,-1)),.4)
 if not hit[0]:hit=tree.find_nearest(Vector((x,y,1.43)))
 p,n,index,dist=hit;q=p+n*.006;lower.append(q);nearest=min((sv[k] for k in sf[index].vertices),key=lambda v:(v.co-p).length_squared);weights.append({suit.vertex_groups[g.group].name:g.weight for g in nearest.groups})
for frac in [.5,1.]:
 for i in range(N):vv.append(tuple(Vector(vv[i]).lerp(lower[i],frac)))
for row in range(2):
 upper=0 if row==0 else base;bottom=base+row*N
 for i in range(N):ff.append((upper+i,bottom+i,bottom+(i+1)%N,upper+(i+1)%N));mi.append(0)
me=bpy.data.meshes.new('BT_HocusPocus_OnePiece_ShoulderFitted');me.from_pydata(vv,[],ff);me.update()
for m in o.data.materials:me.materials.append(m)
o.data=me
for f,m in zip(me.polygons,mi):f.material_index=m;f.use_smooth=True
# New datablock has same original indices; restore complete weights explicitly.
for g in list(o.vertex_groups):o.vertex_groups.remove(g)
head=o.vertex_groups.new(name='head');head.add(list(range(base)),1.,'REPLACE')
for row,frac in enumerate([.5,1.]):
 for i,ww in enumerate(weights):
  idx=base+row*N+i;combined={k:v*frac for k,v in ww.items()};combined['head']=combined.get('head',0)+1-frac;total=sum(combined.values())
  for name,w in combined.items():
   g=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);g.add([idx],w/total,'REPLACE')
o['shoulder_fit']='Continuous flared lower shell projected to actual suit shoulders +6mm; lower cloth weights and transition head blend. Flexible collar interpretation, no separate mask object.'
R['driving_pose']=1.;R['mask_on']=True;R.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Condor_V11_Assembly.blend'),compress=True)
print('ONE_PIECE_SHOULDER_COLLAR_V11_SAVED')
