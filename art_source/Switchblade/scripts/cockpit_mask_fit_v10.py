import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig'];R['in_vehicle']=0.;R['driving_pose']=0.;R['mask_on']=False;R.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
CURRENT=bpy.data.collections['Switchblade_Vehicle'];PARENT=root
# Broad flat keel and softly chamfered lower corners, rather than a rounded bowl.
bpy.data.objects.remove(bpy.data.objects['SB_CabinBelly'],do_unlink=True)
sections=[(0,.63,.80,1.17),(.35,.67,.72,1.20),(1.10,.64,.74,1.23),(1.75,.54,.89,1.30),(2.22,.40,1.13,1.52)]
vv=[];ff=[]
for x,w,lo,hi in sections:vv += [(x,-w,hi),(x,-w,lo+.12),(x,-w*.72,lo),(x,w*.72,lo),(x,w,lo+.12),(x,w,hi)]
for j in range(4):
 for i in range(5):ff.append((j*6+i,j*6+i+1,(j+1)*6+i+1,(j+1)*6+i))
o=mesh('SB_CabinBelly',vv,ff,bpy.data.materials['SB_DeepNavyPaint'],bevel=.035);o.modifiers.new('StructuralHullThickness','SOLIDIFY').thickness=.025
for side in [-1,1]:
 wall=bpy.data.objects['SB_CabinSideWall_'+str(side)]
 for i in [0,1,2]:
  p=wall.data.vertices[i].co;p.z=profile(p.x,[(x,hi) for x,w,lo,hi in sections])-.025;p.y=side*(profile(p.x,[(x,w) for x,w,lo,hi in sections])-.005)
# Rear cabin jamb/gasket fills both the aft side and glass/body seam.
wall=bpy.data.objects['SB_CockpitRearBulkhead']
for v in wall.data.vertices:v.co.y*=1.26
gl=bpy.data.objects['SB_MagentaFacetedGlazing'];pts=[gl.matrix_world@gl.data.vertices[i].co for i in [12,13,14,15]]
vv=[]
for p in pts:
 radial=Vector((0,p.y,p.z-1.85)).normalized();outside=p+radial*.035
 vv += [tuple(p),tuple(outside),tuple(Vector((-.045,outside.y,outside.z))),tuple(Vector((-.045,p.y,p.z)))]
ff=[]
for i in range(4):
 j=(i+1)%4
 for k in range(4):ff.append((i*4+k,j*4+k,j*4+(k+1)%4,i*4+(k+1)%4))
mesh('SB_FittedRearCanopyJamb',vv,ff,bpy.data.materials['SB_EdgeBlue'],bevel=.004)

# Replace a generic gorget ring by a surface fitted to the actual weighted shoulders.
CURRENT=bpy.data.collections['Miles_ViperMask'];PARENT=None
old=bpy.data.objects['MM_Viper_ShoulderGorget'];bpy.data.objects.remove(old,do_unlink=True)
cloth=bpy.data.objects['MM_ContinuousFlightSuit'];dg=bpy.context.evaluated_depsgraph_get();ev=cloth.evaluated_get(dg);me=ev.to_mesh();tree=BVHTree.FromPolygons([v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
base=BVHTree.FromPolygons([v.co for v in cloth.data.vertices],[tuple(p.vertices) for p in cloth.data.polygons])
N=80;layers=7;vv=[];ww=[];ff=[]
for j in range(layers):
 t=j/(layers-1)
 for i in range(N):
  a=2*pi*i/N;target=Vector((.01+.175*cos(a),.265*sin(a),1.39));hit=tree.ray_cast(Vector((target.x,target.y,1.62)),Vector((0,0,-1)),.5)
  if hit[0] is None:hit=tree.find_nearest(target)
  pos,normal,idx,d=hit;outer=pos+normal*.006;inner=Vector((-.015+.108*cos(a),.115*sin(a),1.505-.018*max(0,cos(a))))
  p=inner.lerp(outer,t);p.z+=.008*sin(pi*t);vv.append(tuple(p))
  nearest=base.find_nearest(pos);face=cloth.data.polygons[nearest[2]];vertex=min((cloth.data.vertices[k] for k in face.vertices),key=lambda v:(v.co-pos).length_squared);weights={cloth.vertex_groups[g.group].name:g.weight*t for g in vertex.groups};weights['neck']=weights.get('neck',0)+(1-t);ww.append(weights)
for j in range(layers-1):
 for i in range(N):ff.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
o=mesh('MM_Viper_ShoulderGorget',vv,ff,bpy.data.materials['MM_ViperNavyShell'],smooth=True);o.parent=R
for i,weights in enumerate(ww):
 total=sum(weights.values()) or 1
 for name,w in weights.items():g=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);g.add([i],w/total,'REPLACE')
m=o.modifiers.new('MilesEditableSkin','ARMATURE');m.object=R;m.use_deform_preserve_volume=True;o.modifiers.new('GorgetShellThickness','SOLIDIFY').thickness=.004
for k in ['hide_render','hide_viewport']:drive(o,k,None,'1-m',[('m',R,'mask_on')])
o['fit_method']='Lower edge projected to evaluated shoulder garment at rest; normalized nearest garment weights on outer edge, neck weights inward. Same mesh in both poses.'
gTree=BVHTree.FromPolygons([Vector(v) for v in vv],ff)
for ob in CURRENT.all_objects:
 if ob.type=='MESH' and any(k in ob.name for k in ['CollarBadge','CollarStud','VocalGrille']):
  center=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices);hit=gTree.find_nearest(center)
  if hit[0]:
   delta=hit[0]-center+Vector((.010,0,0))
   for v in ob.data.vertices:v.co+=delta
root['latest_corrections']='V10: inclined nose follows glazing, broad chamfered keel, rear glazing jamb and closed side joints; Viper lower rim follows evaluated shoulders with garment weights.'
R['in_vehicle']=1.;R['driving_pose']=1.;R['mask_on']=True;root.update_tag();R.update_tag();bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V10_Assembly.blend'),compress=True)
print('COCKPIT_AND_SHOULDER_FIT_V10_SAVED')
