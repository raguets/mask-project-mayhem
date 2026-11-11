import bpy,bmesh,json,ast
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Hurricane';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Session_before_motion_v4.blend'),copy=True,compress=True)
exec(compile((A/'scripts/geometry.py').read_text(),'<geometry>','exec'))
ROOT=bpy.data.objects['Hurricane_Control'];R=bpy.data.objects['HondoMacLean_Rig'];LIFT=bpy.data.objects['HU_UpperChassisLift'];ROOF=bpy.data.objects['HU_RoofHinge'];CURRENT=bpy.data.collections['HU_Weapons'];PARENT=LIFT;GROUP='roof_gun'
BLACK=bpy.data.materials['HU_ChassisGraphite'];CHROME=bpy.data.materials['HU_Chrome'];TEAL=bpy.data.materials['HU_TurquoisePaint']
# Advance clear of the fixed rear roof before rising. The final gunner pose is unchanged.
drive(R,'location',0,'a*(-.10+.15*g+.50*min(1,g/.15)*(1-g))',[('a',R,'in_vehicle'),('g',R,'gunner_pose')])
u='min(1,max(0,(g-.18)/.82))';drive(R,'location',2,'a*(.36+.71*('+u+')**2*(3-2*('+u+'))+.30*l)',[('a',R,'in_vehicle'),('g',R,'gunner_pose'),('l',R,'vehicle_lift')])
# Fold the headlight lenses into the front fender pockets before extending barrels.
for sg,label in [(1,'L'),(-1,'R')]:
    lens=bpy.data.objects['HU_HeadlightLensRetract_'+label]
    drive(lens,'location',0,'2.49-.59*min(1,p/.55)',[('p',ROOT,'_lamps')]);drive(lens,'location',1,str(sg)+'*(.79-.02*min(1,p/.55))',[('p',ROOT,'_lamps')]);drive(lens,'location',2,'1+0*p',[('p',ROOT,'_lamps')]);drive(lens,'rotation_euler',1,'1.57079632679*min(1,p/.55)',[('p',ROOT,'_lamps')])
    for o in S.objects:
        if o.type=='MESH' and o.name.startswith('HU_HeadlightCannonCollar_') and label in o.name:
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if len(f.verts)>4],context='FACES');bm.to_mesh(o.data);bm.free()
# A shorter breech clears the fixed rear roof edge; handles slide rearward after opening.
receiver=bpy.data.objects['HU_RoofGunReceiver']
for v in receiver.data.vertices:v.co.x=-.425+(v.co.x+.51)*(.090/.24)
level=bpy.data.objects['HU_RoofGunLevel'];grips=[o for o in level.children if o.name.startswith('HU_RoofGunGrip_')];griproot=empty('HU_RoofGripSlide',parent=level)
drive(griproot,'location',0,'.17*(1-p)',[('p',ROOT,'_roofgun')])
for o in grips:
    mw=o.matrix_world.copy();o.parent=griproot;o.matrix_parent_inverse=griproot.matrix_world.inverted();o.matrix_world=mw
# Cut two real barrel slots and matching hinged lids into the roof panel.
roof=bpy.data.objects['HU_OpeningRoofPanel'];me=bpy.data.meshes.new('HU_OpeningRoofSlotted_Editable');xs=sorted(set(seq(40,-.45,.60)+[-.20]));ys=sorted(set(seq(30,-.64,.64)+[-.23,-.055,.055,.23]));v=[(x,y,1.66+.024*(1-(y/.64)**2)+.031*max(0,1-(y/.66)**2)) for x in xs for y in ys];f=[];N=len(ys)
for i in range(len(xs)-1):
    for j in range(N-1):
        x=(xs[i]+xs[i+1])/2;y=(ys[j]+ys[j+1])/2
        if x<-.20 and .055<abs(y)<.23:continue
        f.append((i*N+j,(i+1)*N+j,(i+1)*N+j+1,i*N+j+1))
me.from_pydata(v,[],f);me.materials.append(TEAL);me.update();roof.data=me
for p in me.polygons:p.use_smooth=True
# Boundary creases for the replacement mesh.
if me.attributes.get('crease_edge'):me.attributes.remove(me.attributes['crease_edge'])
attr=me.attributes.new('crease_edge','FLOAT','EDGE');counts={}
for p in me.polygons:
    for e in p.edge_keys:counts[tuple(sorted(e))]=counts.get(tuple(sorted(e)),0)+1
for e in me.edges:
    if counts[tuple(sorted(e.vertices))]==1:attr.data[e.index].value=1
CURRENT=bpy.data.collections['HU_Body'];GROUP='roof_door'
for sg in [-1,1]:
    y=sg*.23;z=1.66+.024*(1-(y/.64)**2)+.031*(1-(y/.66)**2);lid=empty('HU_RoofCannonSlotLid_'+str(sg),(-.325,y,z),ROOF);drive(lid,'rotation_euler',0,str(-sg*1.57079632679)+'*min(1,r/.12)',[('r',ROOT,'_roof')]);patch('HU_RoofSlotCover_'+str(sg),seq(10,-.45,-.20),seq(8,min(sg*.055,sg*.23),max(sg*.055,sg*.23)),lambda x,y:(x,y,1.66+.024*(1-(y/.64)**2)+.031*(1-(y/.66)**2)),TEAL,root=lid,sub=0,thick=.010,orient=(0,0,1))
# Inner armor has a reserved pocket for the stowed twin gun.
o=bpy.data.objects['HU_RoofInnerArmor'];bpy.data.objects.remove(o,do_unlink=True);GROUP='roof'
for label,x0,x1,y0,y1 in [('Front',-.10,.585,-.615,.615),('Left',-.435,-.10,.24,.615),('Right',-.435,-.10,-.615,-.24)]:box('HU_RoofInnerArmor_'+label,((x0+x1)/2,(y0+y1)/2,1.635),(x1-x0,y1-y0,.025),BLACK,.008,ROOF)
# The saw remains mechanically attached on two telescoping rails.
CURRENT=bpy.data.collections['HU_Weapons'];GROUP='rear_disc';DISC=bpy.data.objects['HU_RearSawSlide']
for y in [-.08,.08]:
    tube('HU_RearSawFixedGuide_'+str(y),(-2.45,y,.315),(-2.04,y,.315),.026,BLACK,root=ROOT)
    tube('HU_RearSawMovingRail_'+str(y),(-2.10,y,.315),(-1.56,y,.315),.015,CHROME,root=DISC)
# Remove paint over the new roof slots; lids are plain turquoise mechanical covers.
decal=bpy.data.objects['HU_RoofFlames'];bm=bmesh.new();bm.from_mesh(decal.data);bad=[]
for face in bm.faces:
    c=face.calc_center_median()
    if c.x<-.20 and .055<abs(c.y)<.23:bad.append(face)
bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(decal.data);bm.free()
for o in S.objects:
    if o.animation_data:
        for fc in o.animation_data.drivers:fc.driver.expression=fc.driver.expression.replace(' + 0.0','')+' + 0.0'
    o.update_tag()
S.frame_set(151);S.frame_set(1);bpy.context.view_layer.update();S.name='Hurricane_V4_Assembly';S['asset']='Hurricane V4 motion fit';S['hidden_mechanism_interpretation']='Lens folding pockets, roof cannon slot lids, sliding handles, saw guides and Hondo transition are interpreted engineering, not measured toy internals.'
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Hurricane_V4_Assembly.blend'),compress=True);print('MOTION_FIT_V4_SAVED')
