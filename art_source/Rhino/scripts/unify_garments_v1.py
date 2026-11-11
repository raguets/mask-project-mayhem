"""Join the knee transition into each weighted garment, preserving the character object."""
import bpy,ast,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;assert not S.get('garments_unified_v1')
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1_before_garment_union.blend'),copy=True,compress=True)
report=[]
for code,person,yy in [('AS','AlexSector_Rig',-.6),('BS','BruceSato_Rig',.6)]:
 r=bpy.data.objects[person];r['driving_pose']=0;r['mask_on']=False;r.location=(0,0,0);r.update_tag();S.frame_set(1);bpy.context.view_layer.update();char=bpy.data.collections[code+'_Character'];suit=bpy.data.objects[code+'_ContinuousFlightSuit'];parts=[suit]+[o for o in char.objects if 'ContinuousKneeFabric' in o.name]
 vv=[];ff=[];weights=[]
 for ob in parts:
  offset=len(vv);vv.extend(v.co.copy() for v in ob.data.vertices);ff.extend(tuple(offset+i for i in f.vertices) for f in ob.data.polygons)
  weights.extend({ob.vertex_groups[g.group].name:g.weight for g in v.groups} for v in ob.data.vertices)
 tree=BVHTree.FromPolygons(vv,ff);me=bpy.data.meshes.new(code+'_ClothUnionInput');me.from_pydata(vv,[],ff);me.update();tmp=bpy.data.objects.new(code+'_ClothUnionWork',me);char.objects.link(tmp)
 mod=tmp.modifiers.new('ContinuousGarmentUnion','REMESH');mod.mode='VOXEL';mod.voxel_size=.003;mod.use_smooth_shade=True
 mod=tmp.modifiers.new('RelaxFabricSeams','SMOOTH');mod.factor=.62;mod.iterations=5
 dg=bpy.context.evaluated_depsgraph_get();ev=tmp.evaluated_get(dg);result=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg);result.name=code+'_ContinuousGarment_Editable';suit.data=result;suit.vertex_groups.clear()
 groupnames=set(k for ww in weights for k in ww)
 groups={name:suit.vertex_groups.new(name=name) for name in groupnames}
 result.materials.clear();result.materials.append(bpy.data.materials[code+'_WovenShirt']);result.materials.append(bpy.data.materials[code+'_TrouserFabric'])
 for v in result.vertices:
  point,normal,index,dist=tree.find_nearest(v.co);blended={};total=0
  for k in ff[index]:
   amount=1/max(.0001,(vv[k]-point).length);total+=amount
   for name,weight in weights[k].items():blended[name]=blended.get(name,0)+weight*amount
  for name,value in blended.items():
   if value/total>.0001:groups[name].add([v.index],value/total,'REPLACE')
 legnames={'pelvis','thigh.L','thigh.R','shin.L','shin.R','foot.L','foot.R'}
 for face in result.polygons:
  pantweight=sum(g.weight for index in face.vertices for g in result.vertices[index].groups if suit.vertex_groups[g.group].name in legnames)/len(face.vertices);face.material_index=int(pantweight>.5 and face.center.z<1.12);face.use_smooth=True
 bpy.data.objects.remove(tmp,do_unlink=True)
 for ob in parts[1:]:bpy.data.objects.remove(ob,do_unlink=True)
 # Brows use their own fiber color, rather than an inherited blond attribute override.
 for ob in char.all_objects:
  if 'Brow_NaturalFibers' in ob.name and ob.type=='MESH':
   color=(.13,.020,.003,1) if code=='AS' else (.008,.006,.004,1)
   for attribute in ob.data.color_attributes:
    for value in attribute.data:value.color=color
 r.location=(2,yy,1.37);r['driving_pose']=1;r.update_tag();report.append({'rig':person,'same_suit_object':suit.name,'vertices':len(result.vertices),'continuous_knee_union':True,'weight_transfer':'Nearest evaluated rest face, inverse-distance blend of its original vertex weights; normalized.'})
S['garments_unified_v1']='Knee bands unioned into existing garment objects at 3mm voxel resolution; skinned weights restored; material regions based on limb groups.'
(A/'garment_union_v1.json').write_text(json.dumps(report,indent=2));S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V1.blend'),compress=True);print('RHINO_GARMENTS_UNIFIED',json.dumps(report))
