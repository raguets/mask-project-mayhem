"""Correct measured pedal gaps after rendered review; save editable V12."""
import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');T=P/'art_source/Thunderhawk';s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig']
r['driving_pose']=1;r['mask_on']=False;r.location=(0,.4,0);r.update_tag();s.frame_set(97);bpy.context.view_layer.update()
def geo(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    vv=[ev.matrix_world@v.co for v in me.vertices];ff=[tuple(f.vertices) for f in me.polygons];ev.to_mesh_clear();return vv,ff
report=[]
for sd,idx in [('R',0),('L',2)]:
    vv,_=geo(bpy.data.objects['MT_BootUpper_'+sd]);pv,pf=geo(bpy.data.objects['THK_Pedal'+str(idx)])
    tr=BVHTree.FromPolygons(pv,pf)
    d,point,nearest=min(((tr.find_nearest(v)[3],v,tr.find_nearest(v)[0]) for v in vv),key=lambda q:q[0])
    shift=(point-nearest)*(1-.0005/d) if d>.0005 else point*0
    for ob in bpy.data.collections['THK11_Interior'].objects:
        if ob.name in ('THK_Pedal'+str(idx),'THK_PedalStem'+str(idx)) or ob.name.startswith('THK_PedalGrip'+str(idx)):ob.location+=shift
    report.append({'boot':sd,'gap_before_m':d,'target_vertex_gap_m':.0005,'pedal_shift':list(shift)})
for ob in s.objects:
    if ob.name.startswith('THK_Pedal'):ob['geometry_note']='Interpreted cockpit; pedal placement fitted to evaluated footwear, no pedal articulation simulated.'
s['V12_InspectionLimits']='193 discrete-frame surface collision audit; no continuous-time volume certification. Seat upholstery/cloth compression not simulated.'
bpy.ops.wm.save_as_mainfile(filepath=str(T/'Thunderhawk_V12.blend'),compress=True)
(T/'pedal_refinement_v12.json').write_text(json.dumps(report,indent=2))
print('V12_MEASURED_PEDAL_GAPS_CORRECTED',json.dumps(report))
