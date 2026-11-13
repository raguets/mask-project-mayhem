import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Switchblade_Control'];CURRENT=bpy.data.collections['Switchblade_Vehicle'];PARENT=root
navy=bpy.data.materials['SB_DeepNavyPaint'];silver=bpy.data.materials['SB_Chrome'];black=bpy.data.materials['SB_BlackMechanism']
bpy.context.scene.frame_set(1);root.update_tag();bpy.context.view_layer.update()
for side in [-1,1]:
 # Leading chine has a broad rear shoulder but stops square ahead of the main wing.
 ob=bpy.data.objects['SB_FixedCockpitChine_'+str(side)]
 points=[(2.52,side*.31),(1.95,side*.74),(.43,side*1.12),(.43,side*.55)]
 for i,v in enumerate(ob.data.vertices):v.co.x,v.co.y=points[i%4]
 # Reproject packed painting to the revised actual panel coordinates.
 uv=ob.data.uv_layers.active
 for f in ob.data.polygons:
  for li in f.loop_indices:
   p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((p.x+.35)/3.0,(abs(p.y)-.25)/.8)
 # User supersedes previous aft-curvature interpretation: road support bends forward.
 st=bpy.data.objects['SB_BentSkidStrut_'+str(side)]
 for v in st.data.vertices:v.co.x=.21-v.co.x
 import bmesh
 bm=bmesh.new();bm.from_mesh(st.data);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(st.data);bm.free()
 # Small, integrated front-wing cannon pod, no loose side-of-glass attachment.
 y=side*.52
 vv=[(1.40,y-.10,1.45),(1.40,y+.10,1.45),(1.40,y+.10,1.565),(1.40,y-.10,1.565),(2.13,y-.075,1.45),(2.13,y+.075,1.45),(2.13,y+.075,1.55),(2.13,y-.075,1.55)]
 ff=[(0,1,2,3),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
 mesh('SB_FrontWingCannonPod_'+str(side),vv,ff,navy,bevel=.018)
 tube('SB_FrontWingCannonCollar_'+str(side),(2.10,y,1.50),(2.145,y,1.50),.070,navy)
 slide=empty('SB_FrontWingCannonSlide_'+str(side),(2.02,y,1.50),root)
 drive(slide,'location',0,'2.02+0.42*t',[('t',root,'transform')])
 tube('SB_FrontWingCannonBarrel_'+str(side),(1.40,y,1.50),(2.135,y,1.50),.043,silver,root=slide)
 tube('SB_FrontWingCannonBore_'+str(side),(2.136,y,1.50),(2.145,y,1.50),.026,black,root=slide)
 # Intake top is modestly higher and wider; base stays attached to the deck.
 for ob in bpy.data.objects:
  if (ob.name.startswith('SB_MetalAirIntake_'+str(side)) or ob.name.startswith('SB_AirIntakeDarkMouth_'+str(side))) and ob.type=='MESH':
   for v in ob.data.vertices:v.co.z=2.12+(v.co.z-2.12)*1.35;v.co.y=side*(.50+(abs(v.co.y)-.50)*1.15)
for ob in bpy.data.objects:
 if ob.name.startswith('SB_AirIntakeVane') and ob.type=='MESH':
  for v in ob.data.vertices:
   side=1 if v.co.y>0 else -1;v.co.z=2.12+(v.co.z-2.12)*1.35;v.co.y=side*(.50+(abs(v.co.y)-.50)*1.15)
# Update the chine paint itself so enlarged aft portions also carry the reference colors.
import numpy as np,json
W=1024;H=512;x,y=np.meshgrid(np.linspace(-.35,2.65,W),np.linspace(.25,1.05,H));rgba=np.empty((H,W,4),dtype=np.float32);rgba[:]=(.016,.043,.095,1)
polys=[([(1.0,.62),(1.65,.62),(.54,1.045),(.48,.95)],(.95,.17,.008)), ([(.70,.76),(1.35,.66),(.52,1.04),(.48,.96)],(.65,.012,.028))]
for pts,color in polys:
 inside=np.zeros((H,W),dtype=bool)
 for i,(ax,ay) in enumerate(pts):
  bx,by=pts[(i+1)%len(pts)];inside ^= ((ay>y)!=(by>y)) & (x<(bx-ax)*(y-ay)/(by-ay+1e-12)+ax)
 rgba[inside,:3]=color
im=bpy.data.images['SB_FrontWingPaint_V16'];im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(A/'textures/SB_FrontWingPaint_V19.png');im.save();im.pack()
root['latest_corrections']='V19: widened/swept front chines end square atX0.43 ahead of main wings; two integrated retractable front-wing cannons; intakes35% taller above deck; supports curve FORWARD (latest user correction), unchanged wider section/rearward patins.'
root.update_tag();bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V19_Assembly.blend'),compress=True)
print('FOREWINGS_CANNONS_INTAKES_FORWARD_SUPPORTS_V19_SAVED')
