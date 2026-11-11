import bpy,bmesh,math,json
from mathutils import Vector,noise
from math import sin,cos,pi,exp
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/Session_before_sculpt_v2.blend'),copy=True,compress=True)
def n(x,y,z=0):return noise.noise(Vector((x,y,z)))
def height(x,y):
    return 8.0+1.8*exp(-((x-6.5)/5.5)**2-((y-5)/6)**2)+.48*n(x*.16,y*.16,4)+.17*n(x*.60,y*.60,2)+.06*n(x*2,y*2,7)
def outline(x,y):
    # The rock remains outside the internal 25.5m hangar envelope.
    left=max(0,min(1,(-x+10)/3.15));right=max(0,min(1,(x-11)/2.95))
    x-=left*(.30+.42*(1+n(y*.19,2,8)));x+=right*(.20+.35*(1+n(y*.17,6,9)))
    return x,y
roof=bpy.data.objects['BH_SandstoneRoof'];NX=68;NY=90
for j in range(NY):
    y=.65+j*37.6/(NY-1)
    for i in range(NX):
        x=-13.15+i*27.1/(NX-1);xx,yy=outline(x,y);roof.data.vertices[j*NX+i].co=(xx,yy,height(x,y))
for side in ['front','back','left','right']:
    ob=bpy.data.objects['BH_SandstoneCliff_'+side];N=100;H=27
    for j in range(H):
        t=j/(H-1)
        for i in range(N):
            q=i/(N-1)
            if side=='front':x=-13.15+q*27.1;y=.65;bottom=6.68
            elif side=='back':x=-13.15+q*27.1;y=38.25;bottom=-.30
            else:x=-13.15 if side=='left' else 13.95;y=.65+q*37.6;bottom=-.30
            xx,yy=outline(x,y);z=bottom+(height(x,y)-bottom)*t
            # Irregular faults and fine horizontal bedding, continuous at the roof.
            fault=(.18*n(q*23,t*3,7)+.06*n(q*61,t*11,4)+.04*sin(z*9+q*6))*(1-t)
            if side in ['front','back']:yy+=(-1 if side=='front' else 1)*fault
            else:xx+=(-1 if side=='left' else 1)*fault
            ob.data.vertices[j*N+i].co=(xx,yy,z)
    ob.data.update()
# Taller broken sandstone pillar with broad asymmetric faces, without regular flutes.
ob=bpy.data.objects['BH_RockColumnOuter'];N=128;H=49
for j in range(H):
    t=j/(H-1);z=8.1+t*3.92;base=3.6-1.05*t+.10*sin(t*8)
    for i in range(N):
        a=i*2*pi/N;r=base+(.27*n(cos(a)*2.2,sin(a)*2.2,t*2)+.07*n(cos(a)*8,sin(a)*8,t*7))*sin(pi*t)
        ob.data.vertices[j*N+i].co=(7+r*cos(a),6+r*sin(a),z+.025*sin(a*5+t))
ob.data.update()
# One detachable irregular cap, same editable mesh and fall controller.
ob=bpy.data.objects['BH_BoulderCapMesh'];rows=[(-1.15,2.42),(-.94,2.62),(-.4,2.57),(.2,2.38),(.7,1.90),(1.10,1.18),(1.30,.02)];N=96
for j,(z,rr) in enumerate(rows):
    for i in range(N):
        a=i*2*pi/N;pert=.17*n(cos(a)*2,sin(a)*2,j*.35)+.055*n(cos(a)*7,sin(a)*7,j*.7);r=rr+pert*sin(pi*j/(len(rows)-1))
        ob.data.vertices[j*N+i].co=(7+r*cos(a),6+r*sin(a),13.22+z+.10*n(cos(a)*3,sin(a)*3,j)*sin(pi*j/(len(rows)-1)))
ob.data.update()
# Replace the degenerate radial centre topology that caused a false triangular highlight.
ob=bpy.data.objects['BH_QuarterRoof'];N=80;v=[(.20,0,6.40),(.20,0,6.23)];f=[]
for r,z in [(11.35,6.40),(12,5.67),(11.35,6.23),(12,5.50)]:v.extend((.20+r*cos(i*pi/2/N),r*sin(i*pi/2/N),z) for i in range(N+1))
a=2;b=a+N+1;c=b+N+1;d=c+N+1
for i in range(N):
    f.extend([(0,a+i,a+i+1),(1,c+i+1,c+i),(a+i,b+i,b+i+1,a+i+1),(b+i,d+i,d+i+1,b+i+1),(c+i,c+i+1,d+i+1,d+i)])
f.extend([(0,1,c,d,b,a),(0,a+N,b+N,d+N,c+N,1)])
old=ob.data;me=bpy.data.meshes.new('BH_QuarterRoof_V2_Editable');me.from_pydata(v,[],f);me.materials.append(bpy.data.materials['BH_ArmorSteel']);me.update();ob.data=me
for mod in list(ob.modifiers):ob.modifiers.remove(mod)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
# World-position colour and bedding give the same stone scale on cap, cliffs and roof.
mat=bpy.data.materials['BH_Sandstone'];ns=mat.node_tree.nodes;ls=mat.node_tree.links;geo=ns.new('ShaderNodeNewGeometry')
for node in list(ns):
    if node.type=='TEX_NOISE':ls.new(geo.outputs['Position'],node.inputs['Vector']);node.inputs['Scale'].default_value=.8 if node.inputs['Detail'].default_value>2 else 2.8
S['BoulderVersion']='V2';S['art_review_note']='V1 render corrected: exposed hangar ceiling, scalloped stone, quarter-roof central shading.'
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V2_Assembly.blend'),compress=True)
print('SCULPT_AND_ROOF_V2_SAVED')
