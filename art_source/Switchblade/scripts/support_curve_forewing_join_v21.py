import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Switchblade'
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
root=bpy.data.objects['Switchblade_Control'];records=[]
for side in [-1,1]:
 ob=bpy.data.objects['SB_BentSkidStrut_'+str(side)]
 # Undo the erroneous whole-part reflection; endpoints again descend FRONT to AFT.
 for v in ob.data.vertices:v.co.x=.21-v.co.x
 import bmesh
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
 pairs=[(0,9),(1,8),(2,7),(3,6),(4,5)];centers=[(ob.data.vertices[i].co+ob.data.vertices[j].co)*.5 for i,j in pairs]
 top=centers[0];bottom=centers[-1];evidence=[]
 for (i,j),center in zip(pairs,centers):
  t=max(0,min(1,(top.z-center.z)/(top.z-bottom.z)));chord_x=top.x+(bottom.x-top.x)*t;new_x=chord_x+.18*math.sin(math.pi*t);delta=new_x-center.x
  ob.data.vertices[i].co.x+=delta;ob.data.vertices[j].co.x+=delta;evidence.append({'z':center.z,'linear_chord_x':chord_x,'actual_center_x':new_x,'forward_convexity_m':new_x-chord_x})
 ob.data.update();records.append({'side':side,'top':list(top),'bottom':list(bottom),'centerline':evidence})
 wing=bpy.data.objects['SB_FixedCockpitChine_'+str(side)]
 for v in wing.data.vertices:
  if abs(v.co.x-.43)<.001:v.co.x=.30
 wing.data.update()
root['support_curve_note']='V21: endpoints descend from front/top to rear/bottom; ONLY convex middle bows forward of their straight chord. Earlier whole-strut reflection corrected, attachment points restored.'
root['forewing_join_note']='V21: straight aft termination X0.30 meets main-wing forward root X0.30; last requested extension13cm, no intentional crossing of panels.'
root.update_tag();bpy.context.scene.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Switchblade_V21_Assembly.blend'),compress=True)
(A/'support_curve_v21.json').write_text(json.dumps(records,indent=2));print('CORRECT_FORWARD_CONVEXITY_AND_JOIN_V21')
