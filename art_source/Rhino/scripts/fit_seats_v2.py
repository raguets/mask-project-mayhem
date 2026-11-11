import bpy,ast,json,shutil
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Rhino';S=bpy.context.scene;assert not S.get('seat_fit_v2')
for yy in [-.6,.6]:
 # Seat under the evaluated garment, with the back brought forward and headrest moved aft.
 for v in bpy.data.objects['RH_SeatCushion_'+str(yy)].data.vertices:v.co.z-=.125
 for v in bpy.data.objects['RH_SeatBack_'+str(yy)].data.vertices:v.co.x+=.035
 for v in bpy.data.objects['RH_SeatHeadrest_'+str(yy)].data.vertices:v.co.x-=.050
 for v in bpy.data.objects['RH_SeatPedestal_'+str(yy)].data.vertices:
  if v.co.z>1.7:v.co.z=1.675
 for sg in [-1,1]:
  ob=bpy.data.objects['RH_SeatStitch_'+str((yy,sg))]
  for spline in ob.data.splines:
   for point in spline.points:
    if point.co.z<2.:point.co.z-=.125
    if point.co.x<1.4:point.co.x+=.035
S['seat_fit_v2']='Cushion lowered 125mm to evaluated garment; back +35mm, headrest aft 50mm. Interpretation, upholstery compression not simulated.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True)
# Repeat the static four-state/cabin checks only; exterior mechanism geometry is unchanged.
tree=ast.parse((A/'scripts/validate_rhino_v2.py').read_text(encoding='utf-8'));functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
namespace={'bpy':bpy,'json':json,'Path':Path,'Vector':Vector,'P':P,'A':A,'S':S,'R':bpy.data.objects['Rhino_Control'],'report':{'characters':{}},'cache':{},'local':{},'pairs':[]}
from mathutils.bvhtree import BVHTree
namespace['BVHTree']=BVHTree;namespace['fixed']=[o.name for o in S.objects if o.name.startswith(('RH_CabRoof','RH_DoorLower_','RH_DoorAFrame_','RH_DoorBFrame_','RH_DoorGlass_','RH_Windshield_'))];namespace['initial_frame']=S.frame_current;namespace['initial_props']={k:namespace['R'][k] for k in ['rear_detach','bullbar','cannons','rear_open','launcher_up','cabinet_slide']};namespace['actor_state']={n:(dict(bpy.data.objects[n].items()),bpy.data.objects[n].location.copy()) for n in ['AlexSector_Rig','BruceSato_Rig']}
exec(compile(ast.Module(body=functions,type_ignores=[]),'<static_cabin_check>','exec'),namespace)
try:namespace['start_characters']()
finally:namespace['restore']()
report=namespace['report'];(A/'cabin_fit_v2.json').write_text(json.dumps(report,indent=2))
assert all(not item['masked_cabin_intersections'] for item in report['characters'].values()),report
previous=json.loads((A/'validation_v2.json').read_text());shutil.copy2(A/'validation_v2.json',A/'validation_v2_before_seat_fit.json');previous['characters']=report['characters'];previous['cabin_check_update']='Static cabin surfaces rechecked after seat/headrest fit; unchanged 241-frame exterior mechanism checks retained.';(A/'validation_v2.json').write_text(json.dumps(previous,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Rhino_V2.blend'),compress=True);print('RHINO_V2_MASKED_CABIN_AND_SEATS_RECHECKED',json.dumps(report))
