"""Inherit shoulder garment weights at the flexible collar's lower edge."""
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;r=bpy.data.objects['MattTrakker_Rig'];suit=bpy.data.objects['MT_ContinuousFlightSuit']
saved=(r['driving_pose'],r['mask_on'],r.location.copy(),s.frame_current)
r['driving_pose']=0;r.location=(0,0,0);r.update_tag();s.frame_set(1);bpy.context.view_layer.update()
vv=[v.co.copy() for v in suit.data.vertices];ff=[tuple(f.vertices) for f in suit.data.polygons];tree=BVHTree.FromPolygons(vv,ff);names={g.index:g.name for g in suit.vertex_groups}
for ob in bpy.data.collections['Spectrum11_Asset'].objects:
    if not ob.name.startswith(('Spectrum_NeckSealConnectingBody','Spectrum_DoubleRedNeckSeal')):continue
    hi=ob.vertex_groups['head'].index;headweights=[sum(g.weight for g in v.groups if g.group==hi) for v in ob.data.vertices];weights=[]
    for v,hw in zip(ob.data.vertices,headweights):
        p,normal,idx,d=tree.find_nearest(v.co);poly=suit.data.polygons[idx];acc={};total=0
        for i in poly.vertices:
            q=1/max(.001,(suit.data.vertices[i].co-p).length)**2;total+=q
            for g in suit.data.vertices[i].groups:acc[names[g.group]]=acc.get(names[g.group],0)+q*g.weight
        norm=sum(acc.values());out={name:(1-hw)*value/norm for name,value in acc.items() if norm};out['head']=out.get('head',0)+hw;weights.append(out)
    ob.vertex_groups.clear();groups={name:ob.vertex_groups.new(name=name) for name in set(n for w in weights for n in w)}
    for i,w in enumerate(weights):
        for name,value in w.items():
            if value>1e-6:groups[name].add([i],value,'REPLACE')
    ob['binding_note']='Upper edge follows head; lower skirt inherits nearby weighted garment surface to maintain shoulder fit in both poses.'
drive,mask,loc,frame=saved;r['driving_pose']=drive;r['mask_on']=mask;r.location=loc;r.update_tag();s.frame_set(frame);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath='G:/DEV/mask-project-mayhem/art_source/Thunderhawk/Thunderhawk_V14.blend',compress=True)
print('V14_COLLAR_SHOULDER_WEIGHT_TRANSFER_SAVED')
