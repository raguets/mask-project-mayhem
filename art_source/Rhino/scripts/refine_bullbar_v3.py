"""V3 bullbar: inspected user toy photo, closed grille-sized cage and vertical bars.
Preserve the same slide/control, vehicle, two characters and previous iterations.
"""
import bpy,bmesh,ast,math,json,re,datetime
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert Path(bpy.data.filepath).name=='Rhino_V2.blend','Inspect and load the saved V2 assembly first.'
assert not (A/'Rhino_V3.blend').exists(),'Do not overwrite an existing reviewed iteration.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/('Session_before_bullbar_V3_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend')),copy=True,compress=True)
R=bpy.data.objects['Rhino_Control'];slide=bpy.data.objects['RH_BullbarSlide'];S.frame_set(1);R.update_tag();bpy.context.view_layer.update()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID'
tree=ast.parse((A/'scripts/build_rhino_v1.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<geometry_helpers>','exec'))
CURRENT=bpy.data.collections['Rhino_Truck'];chrome=bpy.data.objects['RH_GrilleSide_0.82'].data.materials[0];satin=bpy.data.objects['RH_BullbarGuide_1'].data.materials[0]
def points(ob):
 ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();p=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return p
grille=[ob for ob in S.objects if ob.name.startswith(('RH_GrilleSide_','RH_GrilleCross_'))];gv=[p for ob in grille for p in points(ob)];ylo=min(p.y for p in gv);yhi=max(p.y for p in gv);zlo=min(p.z for p in gv);zhi=max(p.z for p in gv)
old_parts=[ob.name for ob in slide.children]
for ob in list(slide.children):bpy.data.objects.remove(ob,do_unlink=True)
for sg in [-1,1]:bpy.data.objects.remove(bpy.data.objects['RH_BullbarGuide_'+str(sg)],do_unlink=True)
def rounded_rectangle(yl,yh,zl,zh,r):
 pts=[]
 for cy,cz,start in [(yh-r,zh-r,0),(yl+r,zh-r,pi/2),(yl+r,zl+r,pi),(yh-r,zl+r,3*pi/2)]:
  pts.extend((cy+r*cos(start+j*pi/2/12),cz+r*sin(start+j*pi/2/12)) for j in range(13))
 return pts
width=.055;outer=rounded_rectangle(ylo,yhi,zlo,zhi,.05);inner=rounded_rectangle(ylo+width,yhi-width,zlo+width,zhi-width,.012);N=len(outer);verts=[]
for x,ring in [(4.92,outer),(4.99,outer),(4.92,inner),(4.99,inner)]:verts.extend((x,y,z) for y,z in ring)
faces=[]
for a,b in [(0,1),(1,3),(3,2),(2,0)]:
 for i in range(N):faces.append((a*N+i,a*N+(i+1)%N,b*N+(i+1)%N,b*N+i))
frame=mesh('RH_BullbarFrame',verts,faces,chrome,bevel=.006)
bm=bmesh.new();bm.from_mesh(frame.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);assert all(e.is_manifold for e in bm.edges);bm.to_mesh(frame.data);bm.free();parent(frame,slide)
frame['reference']='Images de reference/rhino/rhino pare buffle.jpg: toy photograph inspected. Closed rectangular outline, grille-sized. Hidden mounts/dimensions estimated.'
bars=[]
for i in range(7):
 y=ylo+width+(i+1)*(yhi-ylo-2*width)/8
 ob=box('RH_BullbarVertical_'+str(i+1).zfill(2),(4.963,y,(zlo+zhi)/2),(.045,.025,zhi-zlo-.070),chrome,.004);parent(ob,slide);bars.append(ob.name)
# Telescopic supports stay within the bottom border height instead of hanging below it.
new_drivers=[]
for sg in [-1,1]:
 y=sg*.64;z=zlo+width/2
 guide=tube('RH_BullbarGuide_'+str(sg),(0,y,z),(1,y,z),.022,satin);guide.location.x=4.80;parent(guide,R)
 drive(guide,'scale',0,'0.12+0.80*max(v,min(1,max(0,b/0.25)))',[('v',R,'bullbar'),('b',R,'battle_mode')]);new_drivers.append(guide)
 parent(tube('RH_BullbarFixedSleeve_'+str(sg),(4.78,y,z),(4.86,y,z),.034,satin),R)
 parent(box('RH_BullbarFixedMount_'+str(sg),(4.785,y,1.02),(.07,.095,.13),satin,.01),R)
# Explicit reevaluation after all hierarchy and variable links exist.
for ob in new_drivers:
 for f in ob.animation_data.drivers:f.driver.expression=f.driver.expression+' + 0.0'
for frame_number in [1,151,241]:
 S.frame_set(frame_number);R.update_tag();bpy.context.view_layer.update();assert all(f.driver.is_valid for ob in new_drivers+[slide] for f in ob.animation_data.drivers)
S.frame_set(1);bpy.context.view_layer.update();S.name='Rhino_V3_GrilleSizedBullbar';S['asset']='Rhino V3';S['V3_user_request']='Closed bullbar outline and vertical bars, matching cooling grille width/height; supplied rhino pare buffle.jpg inspected.'
report={'source':'Rhino_V2.blend','reference':'Images de reference/rhino/rhino pare buffle.jpg','reference_category':'User-supplied toy photograph, inspected','dimensions_from_existing_model_m':{'width':yhi-ylo,'height':zhi-zlo,'lower_z':zlo,'upper_z':zhi},'estimated_construction':{'frame_band_width_m':width,'frame_depth_m':.070,'vertical_bars':7,'bar_width_m':.025},'same_slide_control':slide.name,'removed_old_parts':old_parts,'new_frame':frame.name,'new_bars':bars,'limits':'Exact toy dimensions and hidden mount geometry are not documented; physical outline matched to current model grille.'}
(A/'bullbar_changes_v3.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V3.blend'),compress=True);print('RHINO_V3_BULLBAR_SAVED',json.dumps(report))
