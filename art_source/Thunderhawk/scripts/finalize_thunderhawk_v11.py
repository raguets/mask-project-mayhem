import bpy,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';S=bpy.context.scene
RIG=bpy.data.objects['MattTrakker_Rig'];CHAR=bpy.data.collections['MT11_Character'];MASK=bpy.data.collections['Spectrum11_Asset'];CURRENT=CHAR;BONES={b.name:True for b in RIG.data.bones}
from math import sin,cos,pi,exp,sqrt
source=(T/'scripts/build_thunderhawk_v11.py').read_text(encoding='utf-8-sig');refine=(T/'scripts/refine_thunderhawk_v11.py').read_text(encoding='utf-8-sig');finish=(T/'scripts/finish_thunderhawk_v11.py').read_text(encoding='utf-8-sig')
helper=source[source.index('def take('):source.index('# Skeleton in')];helper=helper.replace("bpy.context.view_layer.objects.active=ob;ob.select_set(True);", "bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=ob;ob.select_set(True);");exec(helper)
HAIR=bpy.data.materials['MT2_BlondHair'];HAIRHI=bpy.data.materials['MT2_BlondHighlights'];SEAM=bpy.data.materials['MT2_SeamGrey']
haircode=finish[finish.index('# Shorter, flatter'):finish.index('# Recess footwells')]
haircode=haircode.replace(" if z>1.75:\n  rr=sqrt(max(0,1-((z-1.735)/.083)**2));x=-.008+.077*rr*cos(a);y=.075*rr*sin(a)\n",'')
exec(haircode)
# Character remains a single reusable entity with two explicit controls.
for key in ['pose_mode','pose_names']:
 if key in RIG:del RIG[key]
RIG['asset_version']='Matt Trakker V2 / Spectrum V2';RIG['reference_fidelity']='Interpretation of supplied cartoon portrait and toy/replica photographs; visual likeness review, not certified photoreal replica'
for a in list(bpy.data.actions):
 if a.name.startswith('MT_Pose_'):bpy.data.actions.remove(a)
# Helmet shell clears the front face of the headrest; source geometry untouched.
for sd in ['L','R']:
 for ob in bpy.data.collections['THK11_Interior'].objects:
  if ob.name.startswith(('THK_Headrest_'+sd,'THK_HeadrestPost_'+sd)):ob.location.x=-.035
RIG.location=(0,.4,0);RIG['driving_pose']=1;RIG['mask_on']=False;RIG.update_tag();S.frame_set(97);bpy.context.view_layer.update()
# Useful assembly viewport, explicitly chosen in Blender MCP.
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   v=ar.spaces.active.region_3d;v.view_location=(-.1,.2,.75);v.view_distance=4.5;v.view_rotation=(Vector((4,5,2.7))-Vector((-.1,.2,.75))).to_track_quat('Z','Y');v.view_perspective='PERSP';ar.spaces.active.overlay.show_extras=False;ar.spaces.active.shading.color_type='MATERIAL'
S['MT_KnownLimits']='Semi-realistic likeness interpretation; sculpt topology retained, production retopology and final likeness approval pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V11.blend'),compress=True)
# Pose source metadata uses the actual final bone drivers.
meta={'rig':'MattTrakker_Rig','controls':{'driving_pose':{'0':'standing','1':'driving'},'mask_on':{'false':'face visible','true':'Spectrum visible over the same head'}},'rest_bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in RIG.data.bones},'pose_drivers':[{'data_path':f.data_path,'index':f.array_index,'expression':f.driver.expression} for f in RIG.animation_data.drivers]}
(P/'art_source/Matt_Trakker/poses_v2.json').write_text(json.dumps(meta,indent=2))
print('V11_REVIEW_CORRECTIONS_SAVED')

# Corrections from the last inspected renders: no floating part line, clear glass.
part=bpy.data.objects.get('MT_HairPart')
if part:bpy.data.objects.remove(part,do_unlink=True)
import bmesh
for ob in MASK.objects:
 if ob.name.startswith('Spectrum_JawShell'):
  for v in ob.data.vertices:
   z=v.co.z;dep=.119;w=.119
   yy=min(.999,abs(v.co.y)/w);shellx=-.017+dep*sqrt(max(0,1-yy*yy))
   v.co.x=max(v.co.x,shellx+.005)
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
  for f in ob.data.polygons:f.use_smooth=False
m=bpy.data.materials.get('THK11_ClearAutomotiveGlass')
if not m:
 m=bpy.data.materials.new('THK11_ClearAutomotiveGlass');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=next(n for n in n if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.91,.96,1,1);p.inputs['Metallic'].default_value=0;p.inputs['Roughness'].default_value=.025;p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.45
 transparent=n.new('ShaderNodeBsdfTransparent');transparent.inputs['Color'].default_value=(.97,.99,1,1);mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.28;l.new(transparent.outputs[0],mix.inputs[1]);l.new(p.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],next(node for node in n if node.type=='OUTPUT_MATERIAL').inputs['Surface'])
for ob in bpy.data.collections['THK9_Exterior'].objects:
 if ob.type=='MESH' and (ob.name=='THK_Windshield' or ob.name.startswith(('THK_DoorGlass','THK_RearGlass','THK_QuarterGlass','THK_DoorRoofInset'))):ob.data.materials.clear();ob.data.materials.append(m)
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V11.blend'),compress=True)
print('V11_GLASS_AND_LAST_VISIBLE_DEFECTS_CORRECTED')
