"""Reference-led exterior study. All geometry is original, editable and reproducible.
Observed toy images supplied by user; dimensions and kinematics remain estimates.
Run with Blender 5.2. THK_FAST=1 skips rendering, THK_SAMPLES changes render samples.
"""
import bpy, bmesh, math, os, json
from mathutils import Vector
from math import sin, cos, pi, radians
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'renders' / 'v8'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.actions):
    for block in list(datablocks):
        if block.users == 0: datablocks.remove(block)
s = bpy.context.scene
s.unit_settings.system = 'METRIC'
s.unit_settings.scale_length = 1
s.render.fps = 24
s.frame_start, s.frame_end = 1, 193

def material(name, color, metallic=0, roughness=.4):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    p = m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    o = m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(p.outputs['BSDF'], o.inputs['Surface'])
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return m

RED = material('M_THK_Red_V7', (.52,.009,.015), .12, .32)
BLACK = material('M_THK_Trim_V7', (.012,.014,.018), .05, .44)
GLASS = material('M_THK_Glass_V7', (.018,.04,.055), .22, .19)
RUBBER = material('M_THK_Tire_V7', (.012,.013,.016), 0, .72)
SILVER = material('M_THK_Aluminium_V7', (.45,.49,.53), .72, .24)
LENS = material('M_THK_Headlamp_V7', (.61,.69,.72), .3, .22)
AMBER = material('M_THK_Amber_V7', (.9,.35,.025), .1, .3)
TAIL = material('M_THK_Taillamp_V7', (.30,.004,.008), .1, .26)
YELLOW = material('M_THK_Yellow_V7', (.95,.7,.018), .05, .4)
PURPLE = material('M_THK_GridPurple_V7', (.18,.025,.23), 0, .52)
next(n for n in PURPLE.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Specular IOR Level'].default_value=.2
FLOOR = material('M_StudioFloor', (.045,.055,.068), .1, .5)

def empty(name, location=(0,0,0)):
    o = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(o)
    o.location = location
    o.empty_display_type = 'PLAIN_AXES'
    o.empty_display_size = .10
    bpy.context.view_layer.update()
    return o

ROOT_OB = empty('THK_Root')

def parent_keep(o, parent=ROOT_OB):
    bpy.context.view_layer.update()
    world = o.matrix_world.copy()
    o.parent = parent
    o.matrix_world = world
    return o

def mesh(name, verts, faces, mat=RED, parent=ROOT_OB, bevel=0):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    if parent: parent_keep(o, parent)
    if bevel:
        mod = o.modifiers.new('Editable_edge_rounding', 'BEVEL')
        mod.width = bevel; mod.segments = 2
    return o

def cube(name, loc, size, mat=RED, parent=ROOT_OB, bevel=.008):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    parent_keep(o, parent) if parent else None
    if bevel:
        mod = o.modifiers.new('Editable_edge_rounding','BEVEL'); mod.width=bevel; mod.segments=3
    return o

def cylinder(name, loc, radius, depth, mat=SILVER, parent=ROOT_OB, axis='Y', count=48):
    rot = (radians(90),0,0) if axis=='Y' else (0,radians(90),0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=count, radius=radius, depth=depth, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    parent_keep(o,parent) if parent else None
    mod=o.modifiers.new('Rim_bevel','BEVEL'); mod.width=.006; mod.segments=2
    for poly in o.data.polygons:
        if len(poly.vertices)==4: poly.use_smooth=True
    return o

def bar(name, start, end, radius, mat=RED, parent=ROOT_OB):
    a,b=Vector(start),Vector(end)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object; o.name=name; o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    o.data.materials.append(mat); parent_keep(o,parent)
    return o

def solid_sheet(name, verts, faces, mat=RED, parent=ROOT_OB, thickness=.018):
    o=mesh(name,verts,faces,mat,parent)
    # Open surfaces need explicit outward orientation before adding thickness.
    bm=bmesh.new(); bm.from_mesh(o.data)
    reverse=[]
    for face in bm.faces:
        c=face.calc_center_median()
        outward=Vector((c.x,c.y,c.z-.45))
        if face.normal.dot(outward)<0: reverse.append(face)
    if reverse: bmesh.ops.reverse_faces(bm,faces=reverse)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    mod=o.modifiers.new('Editable_shell_thickness','SOLIDIFY'); mod.thickness=thickness; mod.offset=-1
    mod=o.modifiers.new('Shell_edge_rounding','BEVEL'); mod.width=.006; mod.segments=2
    return o

def boolean_cut(o, cutter):
    bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('Construction_cut','BOOLEAN'); mod.object=cutter; mod.operation='DIFFERENCE'; mod.solver='EXACT'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)

# Belt line, flat sides and a chamfered 1980s nose. Wheel arches are real cutouts.
sections=[(-2.15,.86,.81),(-1.85,.92,.86),(-1.1,.93,.88),(.75,.93,.86),(1.5,.92,.79),(2.10,.88,.70),(2.32,.84,.66)]
verts=[]
for x,w,z in sections:
    verts.extend([(x,-w+.05,.28),(x,w-.05,.28),(x,w,.40),(x,w,z-.055),
                  (x,w-.075,z),(x,-w+.075,z),(x,-w,z-.055),(x,-w,.40)])
faces=[tuple(range(7,-1,-1))]
for j in range(len(sections)-1):
    for k in range(8): faces.append((8*j+k,8*j+(k+1)%8,8*(j+1)+(k+1)%8,8*(j+1)+k))
faces.append(tuple(range(8*(len(sections)-1),8*len(sections))))
body=mesh('THK_Body',verts,faces)
for x in (1.40,-1.43):
    cut=cylinder('TEMP_WheelArch',(x,0,.34),.365,2.6,BLACK,None,'Y',64)
    cut.modifiers.clear(); boolean_cut(body,cut)
for sign in (-1,1):
    cut=cube('TEMP_DoorOpening',(-.10,sign*.94,1.0),(2.02,.48,1.08),BLACK,None,0)
    boolean_cut(body,cut)
# Lower the opaque central volume beneath the exterior shell; no cockpit geometry.
cut=cube('TEMP_TubTop',(-.12,0,1.1),(1.90,1.45,1.08),BLACK,None,0)
boolean_cut(body,cut)
for sign in (-1,1):
    cut=cube('TEMP_HeadlampPocket',(2.355,sign*.59,.603),(.16,.37,.135),BLACK,None,0)
    boolean_cut(body,cut)
mod=body.modifiers.new('Body_edge_rounding','BEVEL'); mod.width=.012; mod.segments=3
cube('THK_ExteriorBlackout',(-.12,0,.53),(1.84,1.45,.035),BLACK,bevel=.003)
cube('THK_Sill_L',(-.12,.88,.39),(1.88,.085,.12),SILVER)
cube('THK_Sill_R',(-.12,-.88,.39),(1.88,.085,.12),SILVER)

# Hood, its long raised centre feature and restrained geometric livery.
hoodverts=[(.91,-.73,.865),(.91,.73,.865),(2.25,.75,.694),(2.25,-.75,.694)]
solid_sheet('THK_Hood',hoodverts,[(0,1,2,3)],RED,thickness=.025)
def hood_z(x): return .865+(x-.91)*( .694-.865)/(2.25-.91)
def hood_plane(name, xy, mat, offset=.006):
    return mesh(name,[(x,y,hood_z(x)+offset) for x,y in xy],[tuple(range(len(xy)))],mat)
hood_plane('THK_Hood_CentreRaise',[(1.02,-.22),(1.02,.22),(2.19,.18),(2.19,-.18)],RED,.022)
hood_plane('THK_Hood_Grid_Centre',[(1.09,-.115),(1.09,.115),(2.13,.075),(2.13,-.075)],PURPLE,.026)
for sign,side in [(1,'L'),(-1,'R')]:
    hood_plane('THK_Hood_Grid_'+side,[(1.03,sign*.35),(1.03,sign*.64),(2.16,sign*.63),(2.16,sign*.35)],PURPLE)
    hood_plane('THK_Hood_Lightning_'+side,[(1.11,sign*.46),(1.45,sign*.52),(1.41,sign*.43),(1.80,sign*.50),(1.60,sign*.39),(1.63,sign*.46)],YELLOW,.010)
    for i in range(12):
        x=1.04+i*.099
        hood_plane('THK_Hood_GridLine_%s_%02d'%(side,i),[(x,sign*.35),(x,sign*.64),(x+.005,sign*.64),(x+.005,sign*.35)],BLACK,.008)

# Recessed twin rectangular headlamp units, lower intakes and silver lower bumper.
cube('THK_FrontLowerBumper',(2.325,0,.325),(.10,1.74,.105),SILVER,bevel=.01)
for sign,side in [(1,'L'),(-1,'R')]:
    cube('THK_HeadlampRecess_'+side,(2.291,sign*.59,.603),(.025,.36,.13),BLACK,bevel=.004)
    for j in (-1,1):
        cube('THK_Headlamp_%s_%s'%(side,'A' if j<0 else 'B'),(2.309,sign*.59+j*.083,.606),(.010,.135,.079),LENS,bevel=.005)
    cube('THK_FrontLowerIntake_'+side,(2.34,sign*.37,.418),(.035,.48,.075),BLACK,bevel=.009)
    cube('THK_Indicator_'+side,(2.04,sign*.892,.49),(.22,.02,.055),AMBER,bevel=.005)

# Fixed windshield and hatch glass, with explicit perimeter frames.
frontglass=[(.33,-.60,1.285),(.33,.60,1.285),(.91,.765,.865),(.91,-.765,.865)]
rearGlass=[(-.84,-.60,1.285),(-.84,.60,1.285),(-1.58,.77,.866),(-1.58,-.77,.866)]
for name,poly in [('THK_Windshield',frontglass),('THK_RearGlass',rearGlass)]:
    solid_sheet(name,poly,[(0,1,2,3)],GLASS,thickness=.009)
    for j in range(4): bar(name+'_Frame_'+str(j),poly[j],poly[(j+1)%4],.022,RED)
cube('THK_RoofSpine',(-.255,0,1.29),(1.19,.245,.036),RED,bevel=.012)

# Rear quarter side glass and C-pillars, exterior only.
for sign,side in [(1,'L'),(-1,'R')]:
    poly=[(-.86,sign*.63,1.25),(-1.45,sign*.83,.90),(-1.12,sign*.86,.90)]
    solid_sheet('THK_QuarterGlass_'+side,poly,[(0,1,2)],GLASS,thickness=.008)
    for j in range(3): bar('THK_C_Pillar_%s_%d'%(side,j),poly[j],poly[(j+1)%3],.033,RED)

# Bent door shells: roof leaf, angled window frame, nearly vertical lower side.
for sign,side in [(1,'L'),(-1,'R')]:
    hinge=empty('THK_Wing_Hinge_'+side,(0,sign*.125,1.29)); parent_keep(hinge)
    rows=[(-.80,.27,sign*.145,1.286),(-.82,.28,sign*.60,1.274),
          (-1.02,.83,sign*.842,.905),(-1.025,.80,sign*.885,.485)]
    v=[]
    for a,b,y,z in rows: v.extend([(a,y,z),(b,y,z)])
    shell=solid_sheet('THK_Wing_'+side,v,[(0,1,3,2),(2,3,5,4),(4,5,7,6)],RED,hinge,.025)
    # Glazing follows the true side facet instead of a floating rectangle.
    win=[(-.73,sign*.632,1.227),(.27,sign*.632,1.227),(.69,sign*.815,.951),(-.92,sign*.815,.951)]
    solid_sheet('THK_DoorGlass_'+side,win,[(0,1,2,3)],GLASS,hinge,.006)
    # Roof inset; lower wing/cannon assembly seen in user's images 2,7,9.
    roofpoly=[(-.70,sign*.24,1.299),(.19,sign*.24,1.299),(.21,sign*.53,1.291),(-.70,sign*.53,1.291)]
    solid_sheet('THK_DoorRoofInset_'+side,roofpoly,[(0,1,2,3)],GLASS,hinge,.004)
    rail=cube('THK_CannonSlide_'+side,(-.10,sign*.913,.53),(1.72,.065,.055),SILVER,hinge,.008)
    deploy=empty('THK_CannonDeploy_'+side,(.48,sign*.95,.536)); parent_keep(deploy,hinge)
    cube('THK_CannonBracket_'+side,(.48,sign*.927,.55),(.38,.025,.12),SILVER,deploy,.004)
    cannon=cylinder('THK_DoorCannon_'+side,(.55,sign*.951,.536),.032,.57,SILVER,deploy,'X',24)
    muzzle=cylinder('THK_DoorCannonMuzzle_'+side,(.846,sign*.951,.536),.04,.075,SILVER,deploy,'X',24)
    bore=cylinder('THK_DoorCannonBore_'+side,(.888,sign*.951,.536),.024,.006,BLACK,deploy,'X',20)
    base=deploy.location.copy()
    guide=cube('THK_CannonTelescopicGuide_'+side,(.48,sign*.927,.536),(.38,.025,.02),SILVER,hinge,.003)
    guide_base=guide.location.copy()
    # Slide away from the lower edge of the bent door, along its own rail.
    for fr,travel in [(1,0),(65,0),(97,.18),(121,.18),(151,0),(193,0)]:
        deploy.location=base+Vector((0,0,-travel)); deploy.keyframe_insert(data_path='location',frame=fr)
        guide.location=guide_base+Vector((0,0,-travel/2)); guide.scale.z=(travel+.02)/.02
        guide.keyframe_insert(data_path='location',frame=fr); guide.keyframe_insert(data_path='scale',frame=fr)
    # Red/purple side panel colour block; geometric interpretation, no copied raster.
    patch=[(-.90,sign*.872,.81),(.65,sign*.872,.81),(.63,sign*.887,.65),(-.91,sign*.887,.65)]
    solid_sheet('THK_DoorPurple_'+side,patch,[(0,1,2,3)],PURPLE,hinge,.003)
    bolt=[(-.73,.75),(-.12,.79),(-.23,.71),(.35,.76),(.05,.66),(.10,.73)]
    mesh('THK_DoorLightning_'+side,[(x,sign*(.876+(.81-z)*.09),z) for x,z in bolt],[tuple(range(6))],YELLOW,hinge)
    for fr,angle in [(1,0),(25,0),(97,sign*79),(121,sign*79),(193,0)]:
        hinge.rotation_euler.x=radians(angle); hinge.keyframe_insert(data_path='rotation_euler',frame=fr)

# Wheels with bevelled tires, separate rims and five circular dark spoke pockets.
for x,axle in [(1.40,'F'),(-1.43,'R')]:
    for sign,side in [(1,'L'),(-1,'R')]:
        wheel=cylinder('THK_Wheel_'+axle+side,(x,sign*.873,.335),.322,.224,RUBBER,axis='Y',count=64)
        rim=cylinder('THK_Rim_'+axle+side,(x,sign*.992,.335),.234,.022,SILVER,axis='Y',count=48)
        cylinder('THK_Hub_'+axle+side,(x,sign*1.009,.335),.076,.025,BLACK,axis='Y',count=32)
        for i in range(5):
            a=2*pi*i/5
            cylinder('THK_RimPocket_%s%s_%d'%(axle,side,i),(x+sin(a)*.142,sign*1.008,.335+cos(a)*.142),.055,.010,BLACK,axis='Y',count=20)

# Rounded rectangular twin exhaust mouths, following rear view images (9).
def rounded_rect(w,h,r,n=8):
    points=[]
    for cy,cz,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for j in range(n):
            a=radians(start+j*90/(n-1)); points.append((cy+cos(a)*r,cz+sin(a)*r))
    return points

def nozzle_ring(name,cy,cz,w,h,r,depth,mat):
    outer=rounded_rect(w,h,r); inner=rounded_rect(w-.055,h-.055,max(.018,r-.027))
    v=[]
    for x,ring in [(-2.355,outer),(-2.355,inner),(-2.355+depth,outer),(-2.355+depth,inner)]:
        v.extend([(x,y+cy,z+cz) for y,z in ring])
    n=len(outer); f=[]
    for i in range(n):
        j=(i+1)%n
        f.extend([(i,j,n+j,n+i),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i),(2*n+i,3*n+i,3*n+j,2*n+j)])
    return mesh(name,v,f,mat,bevel=.002)

for sign,side in [(1,'L'),(-1,'R')]:
    nozzle_ring('THK_Reactor_'+side,sign*.49,.406,.49,.225,.09,.18,SILVER)
    darkpoly=rounded_rect(.40,.14,.05)
    mesh('THK_ReactorCavity_'+side,[(-2.20,y+sign*.49,z+.406) for y,z in darkpoly],[tuple(range(len(darkpoly)))],BLACK)
    for i in range(3): cube('THK_ReactorVane_%s_%d'%(side,i),(-2.28,sign*.49+(i-1)*.09,.40),(.10,.016,.075),BLACK,bevel=.003)

# Independent vertical rear fascia and spoiler; no rear-panel rotation.
lift=empty('THK_RearPanel_Lift',(0,0,0)); parent_keep(lift)
rear=cube('THK_RearPanel',(-2.395,0,.425),(.035,1.79,.255),RED,lift,.012)
solid_sheet('THK_RearPanel_TopAndSides',[
    (-2.40,-.895,.553),(-2.40,.895,.553),(-2.38,.895,.553),(-2.38,-.895,.553),
    (-2.40,-.895,.30),(-2.40,.895,.30),(-2.38,.895,.30),(-2.38,-.895,.30)],
    [(0,1,2,3),(0,3,7,4),(1,5,6,2)],RED,lift,.015)
cube('THK_RearFasciaMoulding',(-2.418,0,.435),(.012,1.72,.024),RED,lift,.004)
# The upper tail band is fixed; the smaller bumper slides in front of it in flight.
cube('THK_FixedRearTailBand',(-2.26,0,.73),(.20,1.79,.20),RED,bevel=.012)
cube('THK_FixedRearBridge',(-2.20,0,.58),(.06,1.74,.10),RED,bevel=.005)
for sign,side in [(1,'L'),(-1,'R')]:
    cube('THK_TaillampRecess_'+side,(-2.366,sign*.46,.718),(.012,.65,.057),BLACK,bevel=.004)
    cube('THK_Taillamp_'+side,(-2.375,sign*.46,.718),(.010,.61,.031),TAIL,bevel=.003)
cube('THK_RearLowerTrim',(-2.28,0,.273),(.16,1.68,.06),SILVER,bevel=.008)
cube('THK_RearPlate',(-2.36,0,.304),(.03,.34,.11),BLACK,bevel=.004)
for fr,dz in [(1,0),(45,0),(85,.235),(121,.235),(161,0),(193,0)]:
    lift.location.z=dz; lift.keyframe_insert(data_path='location',frame=fr)

spoiler=empty('THK_Spoiler_Lift'); parent_keep(spoiler)
board=solid_sheet('THK_RearStabilizer',[(-2.11,-.84,.965),(-2.11,.84,.965),(-1.80,.84,.992),(-1.80,-.84,.992)],[(0,1,2,3)],RED,spoiler,.03)
solid_sheet('THK_SpoilerPurple',[(-2.09,-.81,.974),(-2.09,.81,.974),(-1.82,.81,.997),(-1.82,-.81,.997)],[(0,1,2,3)],PURPLE,spoiler,.003)
def spoiler_z(x): return .974+(x+2.09)*(.023/.27)
for i in range(28):
    y=-.81+i*.06
    mesh('THK_SpoilerGridY_%02d'%i,[(-2.09,y,spoiler_z(-2.09)+.003),(-1.82,y,spoiler_z(-1.82)+.003),(-1.82,y+.003,spoiler_z(-1.82)+.003),(-2.09,y+.003,spoiler_z(-2.09)+.003)],[(0,1,2,3)],BLACK,spoiler)
for i in range(6):
    x=-2.085+i*.05
    mesh('THK_SpoilerGridX_%02d'%i,[(x,-.81,spoiler_z(x)+.003),(x,.81,spoiler_z(x)+.003),(x+.003,.81,spoiler_z(x+.003)+.003),(x+.003,-.81,spoiler_z(x+.003)+.003)],[(0,1,2,3)],BLACK,spoiler)
post=cube('THK_SpoilerCentralPost',(-1.91,0,.915),(.15,.13,.075),BLACK,bevel=.006)
for fr,dz in [(1,0),(25,0),(55,.215),(165,.215),(193,0)]:
    spoiler.location.z=dz; spoiler.keyframe_insert(data_path='location',frame=fr)
    post.location.z=.88+(.075+dz)/2; post.scale.z=(.075+dz)/.075
    post.keyframe_insert(data_path='location',frame=fr); post.keyframe_insert(data_path='scale',frame=fr)

# Minor exterior silhouette cues from the supplied toy views.
for sign,side in [(1,'L'),(-1,'R')]:
    hinge=bpy.data.objects['THK_Wing_Hinge_'+side]
    # Return the hinge to road before attaching world-space parts.
    s.frame_set(1)
    mirror=cube('THK_Mirror_'+side,(.65,sign*.91,.96),(.12,.10,.10),RED,hinge,bevel=.025)
    cube('THK_MirrorGlass_'+side,(.59,sign*.918,.966),(.014,.07,.065),SILVER,hinge,bevel=.005)
    bar('THK_MirrorStalk_'+side,(.65,sign*.805,.955),(.65,sign*.91,.96),.016,RED,hinge)

for name,loc in [('SOCKET_DriverSeat',(-.1,.30,.78)),('SOCKET_CameraCockpit',(.25,0,1.13)),('SOCKET_Exhaust',(-2.35,0,.41)),('SOCKET_VFX_Transform',(0,0,.8))]:
    parent_keep(empty(name,loc))
for side,sign in [('L',1),('R',-1)]:
    parent_keep(empty('SOCKET_Muzzle_'+side,(.89,sign*.951,.536)),bpy.data.objects['THK_CannonDeploy_'+side])
for fr,name in [(1,'THK_RoadIdle'),(25,'THK_RoadToFlight'),(97,'THK_FlightIdle'),(121,'THK_FlightToRoad'),(193,'THK_RoadIdle_End')]: s.timeline_markers.new(name,frame=fr)

# Editable reference board, linked to the user's files and excluded from renders/exports.
refcol=bpy.data.collections.new('Reference_Study_UserImages'); s.collection.children.link(refcol)
refcol.hide_render=True; refcol.hide_viewport=True
for i,p in enumerate(sorted((ROOT/'Images reference').glob('*.jpg'))):
    img=bpy.data.images.load(str(p),check_existing=True); img.filepath=bpy.path.relpath(str(p))
    ob=bpy.data.objects.new('REF_'+p.stem,None); refcol.objects.link(ob)
    ob.empty_display_type='IMAGE'; ob.data=img; ob.empty_display_size=2
    ob.location=(7+(i%5)*2.5,0,1+(i//5)*2.5); ob.rotation_euler.x=radians(90)

# A neutral studio with a ground contact and enough fill to judge contours.
s.world=bpy.data.worlds.new('THK_StudioWorld')
s.world.use_nodes=True
s.world.node_tree.nodes.clear()
bg=s.world.node_tree.nodes.new('ShaderNodeBackground'); wo=s.world.node_tree.nodes.new('ShaderNodeOutputWorld')
s.world.node_tree.links.new(bg.outputs['Background'],wo.inputs['Surface'])
bg.inputs['Color'].default_value=(.15,.18,.23,1)
bg.inputs['Strength'].default_value=.45
def aim(o,at): o.rotation_euler=(Vector(at)-o.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(4,-4,6),1300,5),('Fill',(0,5,4),1100,4),('Rear',(-5,-1,4),1500,3)]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); o.location=loc; aim(o,(0,0,.7))
cube('Studio_Floor',(0,0,-.035),(200,200,.04),FLOOR,None,0)
data=bpy.data.cameras.new('THK_RenderCamera'); cam=bpy.data.objects.new('THK_RenderCamera',data); bpy.context.collection.objects.link(cam); s.camera=cam
s.render.engine='CYCLES'; s.cycles.samples=int(os.environ.get('THK_SAMPLES','24'))
s.render.resolution_x=1200; s.render.resolution_y=800; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='AgX'
views=[('front',1,(8,0,.8),(0,0,.8),'ORTHO'),('rear',1,(-8,0,.8),(0,0,.8),'ORTHO'),
       ('side',1,(0,-8,.78),(0,0,.78),'ORTHO'),('top',1,(0,0,8),(0,0,0),'ORTHO'),
       ('perspective',1,(5.9,-6.6,3.7),(0,0,.7),'PERSP'),('flight',97,(5.9,-6.6,3.7),(0,0,.85),'PERSP'),
       ('rear_road',1,(-5.8,-5.8,2.8),(-.4,0,.75),'PERSP'),('rear_flight',97,(-5.8,-5.8,2.8),(-.4,0,.75),'PERSP'),
       ('front_flight',97,(8,0,1),(0,0,1),'ORTHO'),('mid_open',61,(5.9,-6.6,3.7),(0,0,.85),'PERSP'),
       ('mid_return',157,(-5.8,-5.8,2.8),(-.4,0,.75),'PERSP')]
for name,fr,loc,target,typ in views:
    s.frame_set(fr); cam.location=loc; aim(cam,target); data.type=typ; data.ortho_scale=5.4; data.lens=48
    bpy.data.objects['Studio_Floor'].hide_render=(typ=='ORTHO')
    s.render.filepath=str(OUT/(name+'.png'))
    if not os.environ.get('THK_FAST'): bpy.ops.render.render(write_still=True)
s.frame_set(1); cam.location=(5.9,-6.6,3.7); aim(cam,(0,0,.7)); data.type='PERSP'
bpy.data.objects['Studio_Floor'].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Thunderhawk_V8.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in s.objects:
    if ob.name.startswith(('THK_','SOCKET_')) and ob.type in {'MESH','EMPTY'}: ob.select_set(True)
bpy.context.view_layer.objects.active=ROOT_OB
bpy.ops.export_scene.fbx(filepath=str(ROOT/'exports'/'THK_V8.fbx'),use_selection=True,object_types={'EMPTY','MESH'},
                         axis_forward='-Y',axis_up='Z',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,add_leaf_bones=False)
metrics={'version':'V8 reference-led exterior study','objects':sum(o.type=='MESH' and o.name.startswith('THK_') for o in s.objects),
         'frames':[1,193],'fps':24,'cockpit_modeled':False,'dimensions':'estimated metres','references_inspected':10,
         'note':'Toy variants mixed in supplied images; cartoon not validated. Object animation FBX, not a validated skeletal rig.'}
(ROOT/'metrics_v8.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print('THK_V8_COMPLETE',metrics)
