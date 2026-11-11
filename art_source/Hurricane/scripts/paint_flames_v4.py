"""Editable vector-like paint meshes conformed to evaluated body surfaces."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update()
for o in list(S.objects):
    if str(o.get('HU_group','')).startswith('paint_'):bpy.data.objects.remove(o,do_unlink=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
CURRENT=bpy.data.collections['HU_Body'];PARENT=bpy.data.objects['HU_UpperChassisLift'];GROUP='paint_body'
old=bpy.data.materials.get('HU_FlamePaint')
if old and old.users==0:bpy.data.materials.remove(old)
MAT=material('HU_FlamePaint',(.9,.45,.01),.25,.29);n=MAT.node_tree.nodes;l=MAT.node_tree.links;col=n.new('ShaderNodeVertexColor');col.layer_name='FlameTint';l.new(col.outputs['Color'],next(q for q in n if q.type=='BSDF_PRINCIPLED').inputs['Base Color'])
def tint(t):
    t=max(0,min(1,t));a=(.95,.62,.010);b=(.98,.15,.006);c=(.65,.018,.006)
    if t<.35:return a+(1,)
    if t<.85:u=(t-.35)/.50;return tuple(x*(1-u)+y*u for x,y in zip(a,b))+(1,)
    u=(t-.85)/.15;return tuple(x*(1-u)+y*u for x,y in zip(b,c))+(1,)
def rounded(poly):
    pts=[Vector(p) for p in poly];out=[]
    def tangent(i):
        a=pts[(i-1)%len(pts)]-pts[i];b=pts[(i+1)%len(pts)]-pts[i]
        if a.normalized().dot(b.normalized())>.62:return Vector((0,0))
        return (pts[(i+1)%len(pts)]-pts[(i-1)%len(pts)])*.16
    for i,a in enumerate(pts):
        b=pts[(i+1)%len(pts)];c=a+tangent(i);d=b-tangent((i+1)%len(pts))
        for k in range(6):
            t=k/6;p=a*(1-t)**3+3*c*(1-t)**2*t+3*d*(1-t)*t*t+b*t**3;out.append(tuple(p))
    return out
def project_decal(name,source,poly,side,root,flowrange):
    poly=rounded(poly)
    o=bpy.data.objects[source];dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);me=ev.to_mesh();vv=[ev.matrix_world@v.co for v in me.vertices];ff=[list(f.vertices) for f in me.polygons];ev.to_mesh_clear();tree=BVHTree.FromPolygons(vv,ff)
    ring=[Vector((u,v,0)) for u,v in poly];triangles=tessellate_polygon([ring]);verts=[];faces=[];colors=[];N=9
    for indices in triangles:
        tri=[ring[k] if isinstance(k,int) else k for k in indices]
        mapping={}
        for i in range(N+1):
            for j in range(N+1-i):
                p=tri[0]*(1-(i+j)/N)+tri[1]*(i/N)+tri[2]*(j/N);u,v=p.x,p.y
                if side:
                    hit=tree.ray_cast(Vector((u,side*1.3,v)),Vector((0,-side,0)),1.0)
                else:hit=tree.ray_cast(Vector((u,v,2.2)),Vector((0,0,-1)),1.8)
                if hit[0] is None:mapping[i,j]=None;continue
                loc,normal,idx,dist=hit;mapping[i,j]=len(verts);verts.append(tuple(loc+normal*.0013));t=(flowrange[0]-u)/(flowrange[0]-flowrange[1]);t=.80*t+.20*(max(0,min(1,(v-.45)/.6)) if side else abs(v)/.70);colors.append(tint(t))
        for i in range(N):
            for j in range(N-i):
                for ids in [[(i,j),(i+1,j),(i,j+1)]]+([[(i+1,j),(i+1,j+1),(i,j+1)]] if j<N-i-1 else []):
                    kk=[mapping.get(k) for k in ids]
                    if all(k is not None for k in kk):faces.append(kk)
    ob=mesh(name,verts,faces,MAT,root,smooth=True);attr=ob.data.color_attributes.new(name='FlameTint',type='FLOAT_COLOR',domain='POINT')
    for item,c in zip(attr.data,colors):item.color=c
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.000005);bm.to_mesh(ob.data);bm.free()
    sub=ob.modifiers.new('FinePaintTessellation','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=1;sub.render_levels=2
    sw=ob.modifiers.new('ConformedPaint','SHRINKWRAP');sw.target=o;sw.wrap_method='NEAREST_SURFACEPOINT';sw.offset=.0018
    ob['paint_note']='Editable conformed paint geometry, 1.3mm surface offset; original interpretation of flame silhouettes from supplied photographs.'
    return ob
sidepoly=[(2.27,.42),(1.78,.43),(1.12,.45),(1.02,.54),(.65,.48),(.32,.48),(-.08,.58),(-.42,.62),(-.87,.64),(-1.10,.68),(-1.35,.70),(-1.59,.74),(-1.80,.85),(-1.38,.81),(-1.03,.83),(-.68,.85),(-.43,.92),(-.18,.99),(-.42,.87),(-.38,.80),(-.10,.79),(.21,.83),(.43,.93),(.60,1.03),(.48,.87),(.60,.77),(.87,.72),(1.11,.77),(1.40,.90),(1.61,1.03),(1.54,.81),(1.72,.69),(1.93,.64),(2.13,.72),(2.26,.83),(2.24,.67),(2.30,.53)]
for sg,label in [(1,'L'),(-1,'R')]:
    project_decal('HU_SweptFlames_'+label,'HU_SculptedSide_'+label,sidepoly,sg,PARENT,(2.3,-1.8))
    for i,(x,z) in enumerate([(-1.00,.96),(-.35,.94),(.30,1.02)]):project_decal('HU_FlameEmber_'+str((label,i)),'HU_SculptedSide_'+label,[(x+.11,z-.025),(x,z-.041),(x-.105,z+.027),(x-.025,z+.041)],sg,PARENT,(x+.11,x-.105))
hood=[(2.25,-.46),(2.30,.46),(2.08,.41),(1.95,.49),(1.80,.54),(1.84,.40),(1.71,.34),(1.56,.44),(1.36,.49),(1.45,.33),(1.35,.20),(1.11,.18),(1.02,.26),(1.12,.06),(1.31,-.01),(1.39,-.14),(1.28,-.28),(1.09,-.39),(1.38,-.33),(1.60,-.18),(1.74,-.22),(1.78,-.38),(1.63,-.53),(1.90,-.47),(2.02,-.35)]
project_decal('HU_HoodFlames','HU_CurvedHood',hood,0,PARENT,(2.3,1.02))
GROUP='paint_roof';roofpoly=[(.55-(2.3-x)/1.28*.95,y*1.08) for x,y in hood];project_decal('HU_RoofFlames','HU_OpeningRoofPanel',roofpoly,0,bpy.data.objects['HU_RoofHinge'],(.55,-.40))
GROUP='paint_body';trunkpoly=[(-1.20-(2.3-x)/1.28*1.15,y*1.08) for x,y in hood];project_decal('HU_TrunkFlames','HU_CurvedTrunk',trunkpoly,0,PARENT,(-1.20,-2.35))
S['paint_palette']='Turquoise body with yellow-orange-red swept flame paint from supplied Hurricane photographs. Kept separate from silhouette changes.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V4_Assembly.blend'),compress=True);print('HURRICANE_CONFORMED_FLAMES_ADDED')
