"""Inspected 13 November corrections, run inside installed Blender MCP only."""
import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Switchblade_V16_Assembly.blend').exists()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_V16.blend'),copy=True)
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];R=bpy.data.objects['MilesMayhem_Rig'];C=bpy.data.collections['Switchblade_Vehicle'];CURRENT=C;PARENT=root
navy=bpy.data.materials['SB_DeepNavyPaint'];edge=bpy.data.materials['SB_EdgeBlue'];black=bpy.data.materials['SB_BlackMechanism'];silver=bpy.data.materials['SB_Chrome']
s=bpy.context.scene;s.frame_set(121);root.update_tag();bpy.context.view_layer.update()
# Tail fin: vertical trailing edge AFT; swept leading edge forward. Remove exposed pivot cap.
fin=bpy.data.objects['SB_TailRotorToFin']
for o in list(bpy.data.objects):
 if any(o.name.startswith(n) for n in ['SB_VentralTailRotorFin','SB_TailFinOutline','SB_TailRotorHousing','SB_TailRotorGrille']):bpy.data.objects.remove(o,do_unlink=True)
v=[(-4.12,-.04,1.995),(-4.12,-.04,3.15),(-3.88,-.04,3.15),(-3.40,-.04,1.995)]
o=mesh('SB_VentralTailRotorFin',v,[(0,1,2,3)],navy,fin,bevel=.018);o.modifiers.new('FinStructuralThickness','SOLIDIFY').thickness=.08
path('SB_TailFinOutline',v+[v[0]],.009,edge,fin)
# Slim aft-swept, bent patin struts: not the former broad straight triangular plate.
s.frame_set(1);root.update_tag();bpy.context.view_layer.update()
for side in [-1,1]:
 old=bpy.data.objects['SB_BentSkidStrut_'+str(side)];bpy.data.objects.remove(old,do_unlink=True);sk=bpy.data.objects['SB_SkidToCannon_'+str(side)]
 profile_xz=[(.08,1.115),(-.12,1.10),(-.35,.91),(-.53,.64),(-.68,.27),(-.47,.20),(-.39,.49),(-.23,.75),(-.035,.94),(.13,1.015)]
 vv=[(x,side*(.70+.28*max(0,min(1,(1.115-z)/.915))),z) for x,z in profile_xz]
 ob=mesh('SB_BentSkidStrut_'+str(side),vv,[tuple(range(len(vv)))],navy,sk,bevel=.026);ob.modifiers.new('SweptStrutThickness','SOLIDIFY').thickness=.065
# Wider actual blades; index/fold finishes before secondary base descent.
for side in [-1,1]:
 for name in ['SB_MainRotorBlade_'+str(side),'SB_BladeTipMark_'+str(side)]:
  for v in bpy.data.objects[name].data.vertices:v.co.y*=1.30
 h=bpy.data.objects['SB_BladeFold_'+str(side)]
 drive(h,'rotation_euler',2,str(side)+'*1.57079632679*(1-min(1,t/0.82))',[('t',root,'transform')])
mast=bpy.data.objects['SB_MainRotorMast']
drive(mast,'location',2,'2.34-0.13*min(1,max(0,(t-0.82)/0.18))',[('t',root,'transform')])
# Remove floating side trim and detached square housings, retain mechanism in integral shoulders.
removed=[]
for ob in list(bpy.data.objects):
 if any(ob.name.startswith(n) for n in ['SB_FrontChromePort','SB_GunHousing','SB_GunCoolingRib']):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
for side in [-1,1]:
 gun=bpy.data.objects['SB_SideGunSlide_'+str(side)]
 drive(gun,'location',0,'-0.15+0.44*t',[('t',root,'transform')]);drive(gun,'location',1,str(side)+'*0.75',[('t',root,'transform')])
 vv=[(-.40,side*.48,1.52),(-.40,side*.71,1.52),(.10,side*.74,1.52),(.10,side*.50,1.52),(-.40,side*.48,2.12),(-.40,side*.73,2.12),(.10,side*.78,2.02),(.10,side*.50,2.02)]
 ff=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 mesh('SB_IntegratedShoulder_'+str(side),vv,ff,navy,bevel=.03)
 tube('SB_FixedCannonGuide_'+str(side),(-.28,side*.75,1.95),(.13,side*.75,1.95),.068,black)
# Two metal air scoops at upper mid-fuselage, attached to the deck and open forward.
for side in [-1,1]:
 vv=[(-.27,side*.39,2.125),(-.27,side*.61,2.125),(-.27,side*.61,2.23),(-.27,side*.39,2.23),(-1.15,side*.42,2.12),(-1.15,side*.57,2.12),(-1.15,side*.57,2.155),(-1.15,side*.42,2.155)]
 ff=[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0),(4,7,6,5)]
 mesh('SB_MetalAirIntake_'+str(side),vv,ff,silver,bevel=.012)
 mesh('SB_AirIntakeDarkMouth_'+str(side),[(-.279,side*.405,2.14),(-.279,side*.595,2.14),(-.279,side*.595,2.215),(-.279,side*.405,2.215)],[(0,1,2,3)],black)
 for y in [.435,.49,.545]:tube('SB_AirIntakeVane',(-.265,side*y,2.141),(-.265,side*y,2.213),.0045,silver,N=12)
# Angular rising keel; nose underside keeps substance instead of ending in a thin sheet.
for name in ['SB_CabinBelly','SB_NoseWedge']:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
sections=[(0,.63,.88,1.17),(.35,.67,.90,1.20),(1.10,.64,.91,1.23),(1.75,.54,1.025,1.30),(2.22,.40,1.085,1.52)]
vv=[];ff=[]
for x,w,lo,hi in sections:vv += [(x,-w,hi),(x,-w,lo+.075),(x,-w*.66,lo),(x,w*.66,lo),(x,w,lo+.075),(x,w,hi)]
for j in range(4):
 for i in range(5):ff.append((j*6+i,j*6+i+1,(j+1)*6+i+1,(j+1)*6+i))
o=mesh('SB_CabinBelly',vv,ff,navy,bevel=.018);o.modifiers.new('KeelWall','SOLIDIFY').thickness=.022
ns=[(2.22,.40,1.085,1.60),(2.50,.33,1.11,1.53),(2.95,.15,1.14,1.27),(3.12,.04,1.14,1.24)]
vv=[];ff=[]
for x,w,lo,hi in ns:vv += [(x,-w*.7,lo),(x,w*.7,lo),(x,w,(lo+hi)/2),(x,w*.7,hi),(x,-w*.7,hi),(x,-w,(lo+hi)/2)]
for j in range(3):
 for i in range(6):ff.append((j*6+i,j*6+(i+1)%6,(j+1)*6+(i+1)%6,(j+1)*6+i))
ff += [tuple(reversed(range(6))),tuple(range(18,24))];mesh('SB_NoseWedge',vv,ff,navy,bevel=.012)
# Raise only pedal/feet contact; same body and head remain under the unchanged canopy.
for ob in bpy.data.collections['Switchblade_Interior'].all_objects:
 if ob.name.startswith('SB_RudderPedal') or ob.name=='SB_CockpitFloor':ob.location.z+=.16
R['driving_pose']=1.;R.update_tag();bpy.context.view_layer.update()
leg_names=['thigh.L','shin.L','foot.L','thigh.R','shin.R','foot.R']
for f in list(R.animation_data.drivers):
 if any(('pose.bones["'+n+'"]') in f.data_path for n in leg_names):R.driver_remove(f.data_path,f.array_index)
for n in leg_names:R.pose.bones[n].rotation_quaternion=(1,0,0,0)
bpy.context.view_layer.update()
def orient(n,start,end):
 b=R.pose.bones[n];rest=R.data.bones[n];q=(rest.tail_local-rest.head_local).rotation_difference(Vector(end)-Vector(start));mat=(q.to_matrix()@rest.matrix_local.to_3x3()).to_4x4();mat.translation=start;b.matrix=mat;bpy.context.view_layer.update()
for side,label in [(1,'L'),(-1,'R')]:
 upper='thigh.'+label;lower='shin.'+label;a=R.pose.bones[upper].head.copy();target=Vector((.58,side*.18,.86));axis=(target-a).normalized();L1=R.data.bones[upper].length;L2=R.data.bones[lower].length;d=(target-a).length;x=(L1*L1-L2*L2+d*d)/(2*d);h=math.sqrt(max(0,L1*L1-x*x));bend=Vector((1,side*.2,0));bend=(bend-axis*bend.dot(axis)).normalized();knee=a+axis*x+bend*h;orient(upper,a,knee);orient(lower,knee,target);b=R.pose.bones['foot.'+label];p=b.head.copy();orient(b.name,p,p+Vector((.14,0,-.015)))
for name in leg_names:
 b=R.pose.bones[name];q=list(b.rotation_quaternion)
 for i,val in enumerate(q):drive(b,'rotation_quaternion',i,str((1,0,0,0)[i])+'*(1-p)+'+str(val)+'*p',[('p',R,'driving_pose')])
# Flush reference-based orange/red paint on main wings and BOTH front chines, packed UV images.
def painted(name,objects,polygons,extent,W=512,H=1024):
 xmin,xmax,ymin,ymax=extent;x,y=np.meshgrid(np.linspace(xmin,xmax,W),np.linspace(ymin,ymax,H));rgba=np.zeros((H,W,4),dtype=np.float32);rgba[:,:,:3]=(.016,.043,.095);rgba[:,:,3]=1
 for points,color in polygons:
  inside=np.zeros((H,W),dtype=bool)
  for i,(ax,ay) in enumerate(points):
   bx,by=points[(i+1)%len(points)];inside ^= ((ay>y)!=(by>y)) & (x<(bx-ax)*(y-ay)/(by-ay+1e-12)+ax)
  rgba[inside,:3]=color;rgba[inside,3]=1
 im=bpy.data.images.new(name,width=W,height=H,alpha=True);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(A/'textures'/str(name+'.png'));im.file_format='PNG';im.save();im.pack()
 mat=navy.copy();mat.name=name+'_Paint';nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');tex=nodes.new('ShaderNodeTexImage');tex.image=im;nodes.active=tex;tex.select=True;mix=nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.016,.043,.095,1);links.new(tex.outputs['Alpha'],mix.inputs[0]);links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
 for ob in objects:
  ob.data.materials.clear();ob.data.materials.append(mat);uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='ReferencePaintUV')
  for face in ob.data.polygons:
   for li in face.loop_indices:
    p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((p.x-xmin)/(xmax-xmin),(abs(p.y)-ymin)/(ymax-ymin))
 return {'name':name,'polygons':polygons,'extent':extent}
orange=(.95,.17,.008);red=(.65,.012,.028)
main=[([(-.015,.90),(-.43,2.75),(-.66,2.31),(-.37,1.03)],orange),([(-.26,1.00),(-.57,2.45),(-.79,2.65),(-.51,1.14)],red)]
front=[([(.19,.77),(.72,.66),(.45,.84),(.12,.94)],orange),([(.31,.79),(.62,.71),(.35,.89),(.11,.94)],red)]
paints=[painted('SB_MainWingPaint_V16',[bpy.data.objects['SB_MainWing_'+str(i)] for i in [-1,1]],main,(-1.10,.25,.60,3.95)),painted('SB_FrontWingPaint_V16',[bpy.data.objects['SB_FixedCockpitChine_'+str(i)] for i in [-1,1]],front,(-.35,2.65,.25,1.05),1024,512)]
for ob in list(bpy.data.objects):
 if ob.name.startswith('SB_ChineFlash'):bpy.data.objects.remove(ob,do_unlink=True)
(A/'textures/paint_polygons_v16.json').write_text(json.dumps(paints,indent=2))
root['latest_corrections']='V16: concealed fin pivot, correctly swept forward/flat aft fin, aft-swept narrow patin struts, full wing/chine paints, wider blades and post-fold base drop, angular rising keel/thicker nose, no detached side trim, two upper metal air intakes. Hidden structure dimensions estimated.'
root['rotor_stow_sequence']='Blade fold completes at82%; base descends13cm during82–100%. Same persistent blades, chord widened30%.'
root.update_tag();R.update_tag();s.frame_set(1);bpy.context.view_layer.update()
for scr in bpy.data.screens:
 for ar in scr.areas:
  if ar.type=='VIEW_3D':ar.spaces.active.shading.color_type='TEXTURE'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V16_Assembly.blend'),compress=True)
print('V16_USER_CORRECTIONS_SAVED','removed',removed)
