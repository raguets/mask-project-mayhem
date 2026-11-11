"""Diagnostic evaluated triangle checks; not a universal volume-clearance proof."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
S=bpy.context.scene;R=bpy.data.objects['CalhounBurns_Rig'];root=bpy.data.objects['Raven_Control'];A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
saved=(S.frame_current,R['driving_pose'],R['mask_on'],R['in_vehicle'],root['hover_height'])
def tree(name):
    ob=bpy.data.objects[name];dg=bpy.context.evaluated_depsgraph_get();evaluated=ob.evaluated_get(dg);me=evaluated.to_mesh();verts=[evaluated.matrix_world@v.co for v in me.vertices];faces=[tuple(f.vertices) for f in me.polygons];result=BVHTree.FromPolygons(verts,faces);evaluated.to_mesh_clear();return result
def bounds(name):
    ob=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[ob.matrix_world@Vector(c) for c in ob.bound_box];return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
report={'method':'Evaluated mesh triangle intersections, with separate state/identity/bounds measurements; no full volume containment certification.','frames':[],'states':[]}
R['driving_pose']=1;R['in_vehicle']=1;R['mask_on']=True;root['hover_height']=0
for frame in [1,46,61,76,91,106,121,151]:
    S.frame_set(frame);R.update_tag();bpy.context.view_layer.update();pairs=[]
    for wheel in ['L','R']:
        for first,second in [('RV_Hood_ReverseArmor','RV_FrontTire_'+wheel),('RV_Hood_OuterSkin','RV_FrontTire_'+wheel),('RV_Hood_OuterSkin','RV_HoodBayArmoredDeck'),('RV_RearTire_'+wheel,'RV_RearUndertray'),('RV_RearTire_'+wheel,'RV_WheelWellBulkhead_'+wheel+'-1.22')]:
            count=len(tree(first).overlap(tree(second)))
            if count:pairs.append({'a':first,'b':second,'triangle_pairs':count})
    report['frames'].append({'frame':frame,'transform':root['transform'],'intersections':pairs})
for d in [0,1]:
    for m in [False,True]:
        R['driving_pose']=d;R['mask_on']=m;R['in_vehicle']=d;R.update_tag();S.frame_set(1);bpy.context.view_layer.update()
        report['states'].append({'driving':d,'mask':m,'head_mesh':bpy.data.objects['CB_Head_AnatomicalSurface'].data.name,'suit_mesh':bpy.data.objects['CB_ContinuousFlightSuit'].data.name,'head_bounds':bounds('CB_Head_AnatomicalSurface'),'helmet_bounds':bounds('CB_ClosedHelmetShell'),'roof_bounds':bounds('RV_RoofTarga')})
report['remaining_intersection_frames']=[f['frame'] for f in report['frames'] if f['intersections']]
S.frame_set(saved[0]);R['driving_pose'],R['mask_on'],R['in_vehicle'],root['hover_height']=saved[1:];R.update_tag();bpy.context.view_layer.update()
(A/'geometry_audit_v2.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
