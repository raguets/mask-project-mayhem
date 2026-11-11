"""High mountain backing, simple rectangular forecourt; user corrections 2026-11-05."""
import bpy,bmesh,math,json,random,ast
from pathlib import Path
from mathutils import Vector,noise
from math import sin,cos,pi,exp
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
def n(x,y,z=0):return noise.noise(Vector((x,y,z)))
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def front(x):return .65+.017*max(0,abs(x-1)-15)**2
def height(x,y):
    rise=smooth((y-7)/12)
    peaks=35*exp(-((x+9)/25)**2-((y-40)/31)**2)+28*exp(-((x-23)/19)**2-((y-72)/26)**2)+22*exp(-((x+27)/19)**2-((y-85)/27)**2)
    crag=(2.8*n(x*.12,y*.08,1)+1.2*n(x*.35,y*.25,3)+.35*n(x*1.1,y*.75,4))*(.2+.8*rise)
    taper=smooth((65-abs(x-2))/18)*smooth((125-y)/20)
    return .10+taper*(8.5+rise*peaks+crag)
def replace(name,v,f,material=None,smooth_faces=True):
    ob=bpy.data.objects[name];old=ob.data;me=bpy.data.meshes.new(name+'_V3_Editable');me.from_pydata(v,[],f)
    me.materials.append(material or old.materials[0]);me.update()
    for poly in me.polygons:poly.use_smooth=smooth_faces
    ob.data=me;return ob
# Real mountain, roughly 125m wide and 125m deep, rising over 40m behind the base.
NX=211;NY=201;v=[];f=[]
for j in range(NY):
    t=j/(NY-1)
    for i in range(NX):
        x=-60+i*125/(NX-1);y=front(x)+(125-front(x))*t;v.append((x,y,height(x,y)))
for j in range(NY-1):
    for i in range(NX-1):
        ids=(j*NX+i,j*NX+i+1,(j+1)*NX+i+1,(j+1)*NX+i);c=sum((Vector(v[k]) for k in ids),Vector())/4
        if (c.x-7)**2+(c.y-6)**2<2.88**2:continue
        # Alternating triangles retain broken geological facets rather than a planar slab.
        f.extend([(ids[0],ids[1],ids[2]),(ids[0],ids[2],ids[3])])
replace('BH_SandstoneRoof',v,f)
for side in ['front','back','left','right']:
    vv=[];ff=[];N=211;H=36
    for j in range(H):
        t=j/(H-1)
        for i in range(N):
            q=i/(N-1)
            if side in ['front','back']:
                x=-60+125*q;y=front(x) if side=='front' else 125
            else:
                x=-60 if side=='left' else 65;y=front(x)+(125-front(x))*q
            bottom=-.30
            if side=='front':bottom=-.30+6.98*smooth((x+16)/2)*smooth((17-x)/2)
            z=bottom+(height(x,y)-bottom)*t
            # Faulted front cliffs, connected precisely to the terrain along the upper edge.
            out=(.22*n(q*29,t*5,8)+.08*n(q*90,t*12,2))*(1-t)
            if side in ['front','back']:y+=(-1 if side=='front' else 1)*out
            else:x+=(-1 if side=='left' else 1)*out
            vv.append((x,y,z))
    for j in range(H-1):ff.extend((j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i) for i in range(N-1))
    replace('BH_SandstoneCliff_'+side,vv,ff)
# Layered irregular promontory remains in front of the much taller mountain.
ob=bpy.data.objects['BH_RockColumnOuter'];N=128;H=49
profile=[(0,7.2),(.15,6.5),(.23,5.5),(.44,5.7),(.52,4.2),(.70,4.0),(.80,3.0),(1,2.55)]
for j in range(H):
    t=j/(H-1);z=6.72+t*5.30
    for k in range(len(profile)-1):
        if profile[k][0]<=t<=profile[k+1][0]:
            a,ra=profile[k];b,rb=profile[k+1];base=ra+(rb-ra)*smooth((t-a)/(b-a));break
    for i in range(N):
        a=i*2*pi/N;pert=.50*n(cos(a)*2.8,sin(a)*2.8,t*1.7)+.11*n(cos(a)*10,sin(a)*10,t*4);r=base+pert*sin(pi*t)
        ob.data.vertices[j*N+i].co=(7+r*cos(a),6+r*sin(a),z+.025*sin(a*5+t))
ob.data.update()
cap=bpy.data.objects['BH_BoulderCapMesh'];rows=[(-1.15,2.42),(-.94,2.62),(-.4,2.57),(.2,2.38),(.7,1.90),(1.10,1.18),(1.30,.02)];N=96
for j,(z,rr) in enumerate(rows):
    for i in range(N):
        a=i*2*pi/N;envelope=sin(pi*j/(len(rows)-1));r=rr+(.32*n(cos(a)*2,sin(a)*2,j*.35)+.10*n(cos(a)*7,sin(a)*7,j*.7))*envelope
        cap.data.vertices[j*N+i].co=(7+r*cos(a),6+r*sin(a),13.22+z+.16*n(cos(a)*3,sin(a)*3,j)*envelope)
cap.data.update()
# No road: only one rectangular concrete/asphalt plinth in front of the base.
ob=bpy.data.objects.get('BH_ExitApron')
if ob:bpy.data.objects.remove(ob,do_unlink=True)
outline=[(-14,-23),(20,-23),(20,0),(-14,0)];v=[(x,y,z) for z in [-.30,0] for x,y in outline];f=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)]
replace('BH_StationSlab',v,f,smooth_faces=False)
# End demonstration travel on the slab, after the full vehicle has cleared the gate.
tree=ast.parse((P/'art_source/Boulder_Hill/scripts/build_base_v1.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='exit_route')
code=ast.unparse(fn).replace('* 15','* 8');exec(code)
meta={}
for label,y in [('Thunderhawk',15),('Rhino',33)]:
    pts,length=exit_route(y);route=bpy.data.objects['BH_'+label+'_ExitRoute'];sp=route.data.splines[0]
    for p,xyz in zip(sp.points,pts):p.co=(*xyz,1)
    gate=Vector((.2+12/2**.5,-12/2**.5,0));target=gate+Vector((1,-1,0)).normalized()*1.2
    nearest=min(range(len(pts)),key=lambda i:(Vector(pts[i])-target).length)
    meta[label]={'bay_y':y,'samples':pts,'path_length_m':length,'review_progress':nearest/240,'review_frame':round((211 if label=='Thunderhawk' else 351)+(120 if label=='Thunderhawk' else 180)*nearest/240)}
(P/'art_source/Boulder_Hill/exit_routes_v3.json').write_text(json.dumps(meta,indent=2))
# Keep metal reflections broad and avoid the geometric-looking highlight from the large area lamp.
roof=bpy.data.objects['BH_QuarterRoof'];mat=bpy.data.materials['BH_ArmorSteel'].copy();mat.name='BH_QuarterRoofSatin';p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.58;roof.data.materials[0]=mat
ground=bpy.data.objects['BH_DesertGround']
for v in ground.data.vertices:v.co.x=4+(v.co.x-4)*8;v.co.y=5+(v.co.y-5)*8
for o in S.objects:
    if o.animation_data:
        for fc in o.animation_data.drivers:fc.driver.expression+=' + 0.0'
    o.update_tag()
S['mountain_note']='Base backed into an interpreted high sandstone mountain, not a flat rock roof. Supplied cartoon cliff and user correction 2026-11-05.'
S['forecourt_note']='Simple rectangular slab, no exit road.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V3_Assembly.blend'),compress=True)
print('MOUNTAIN_SLAB_V3_SAVED',max(v.co.z for v in bpy.data.objects['BH_SandstoneRoof'].data.vertices),{k:v['review_frame'] for k,v in meta.items()})
