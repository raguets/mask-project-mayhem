import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');s=bpy.context.scene
co=bpy.data.collections.new('MT10_References');s.collection.children.link(co);co.hide_render=True;co.hide_viewport=True
for i,p in enumerate(sorted((P/'Images de reference/Matt Trakker').glob('*.jpg'))):
 im=bpy.data.images.load(str(p),check_existing=True);im.pack()
 ob=bpy.data.objects.new('REF_MT_'+p.stem,None);co.objects.link(ob);ob.empty_display_type='IMAGE';ob.data=im;ob.location=(i*.5,4,1);ob.empty_display_size=.4
# Audit every frame, including intermediate interpolation.
rows=[]
for fr in range(1,194):
 s.frame_set(fr);x=bpy.data.objects['THK_Reactor_Deploy_L'].location.x;z=bpy.data.objects['THK_RearPanel_Lift'].location.z
 if x<-.00001:assert abs(z-.215)<.00001,(fr,x,z)
 if fr in [1,45,85,91,97,121,127,133,173,193]:rows.append({'frame':fr,'reactor_x':x,'panel_z':z})
report={'frames_checked':193,'clearance_timing_pass':True,'reactor_travel_m_estimated':.085,'character_objects':len(bpy.data.collections['MT10_Character'].objects),'reference_images_packed':8,'interior_complete':False,'production_rig':False,'samples':rows}
(P/'art_source/Thunderhawk/validation_v10.json').write_text(json.dumps(report,indent=2))
s.frame_set(97)
for screen in bpy.data.screens:
 for ar in screen.areas:
  if ar.type=='VIEW_3D':
   v=ar.spaces.active.region_3d;v.view_location=(-.1,.25,.8);v.view_distance=3.8;v.view_rotation=(Vector((4,5,2.8))-Vector((-.1,.25,.8))).to_track_quat('Z','Y');v.view_perspective='PERSP'
   ar.spaces.active.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Thunderhawk/Thunderhawk_V10.blend'),compress=True)
print(json.dumps(report))
