import bpy, math, os
from mathutils import Vector
from math import radians
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1; s.render.fps=24; s.frame_start=1; s.frame_end=193

def mat(n,c,metal=0,rough=.4):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True; m.node_tree.nodes.clear(); p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled'); out=m.node_tree.nodes.new('ShaderNodeOutputMaterial'); m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
red=mat('M_THK_Red',(.52,.012,.018),.35); dark=mat('M_THK_Glass',(.018,.035,.05),.3,.18); rubber=mat('M_THK_Rubber',(.014,.016,.018),0,.7); metal=mat('M_THK_Metal',(.32,.35,.37),.7); lamp=mat('M_THK_Lamp',(.8,.72,.46),.1)
def mesh(n,verts,faces,m):
 me=bpy.data.meshes.new(n); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new(n,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(m); return ob
def profile(n,sections,m):
 # sections x, half-width, bottom, top
 v=[]
 for x,w,b,t in sections: v += [(x,-w,b),(x,w,b),(x,w,t),(x,-w,t)]
 f=[(3,2,1,0)]
 for i in range(len(sections)-1):
  a=4*i; b=a+4
  for j in range(4): f.append((a+j,a+(j+1)%4,b+(j+1)%4,b+j))
 f.append(tuple(range(4*(len(sections)-1),4*len(sections))))
 return mesh(n,v,f,m)
def cube(n,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); return o
def empty(n,loc):
 o=bpy.data.objects.new(n,None); bpy.context.collection.objects.link(o); o.location=loc; o.empty_display_type='PLAIN_AXES'; o.empty_display_size=.15; return o
root=empty('THK_Root',(0,0,0))
body=profile('THK_Body',[(-2.35,.78,.31,.75),(-2.05,.91,.30,.87),(-1.25,.93,.30,.90),(.80,.92,.30,.85),(1.75,.88,.29,.70),(2.32,.73,.30,.54)],red); body.parent=root
# roof and dark exterior glazing; no interior
roof=profile('THK_Roof',[(-1.32,.69,.87,1.00),(-.77,.67,1.28,1.31),(.32,.66,1.30,1.33),(.95,.70,.85,.88)],dark); roof.parent=root
roofstrip=cube('THK_Roof_Spine',(-.2,0,1.32),(1.15,1.27,.045),red); roofstrip.parent=root
# wings/doors attached at roof edge; outer edge sweeps outward as rotated around local X
for side,sign in [('L',1),('R',-1)]:
 hinge=empty('THK_Wing_Hinge_'+side,(-.05,sign*.68,1.16)); hinge.parent=root
 # local coords, door panel from top hinge out and downward
 v=[(-.85,0,0),(.76,0,0),(.88,sign*.23,-.58),(-.9,sign*.23,-.58),(-.85,sign*.035,0),(.76,sign*.035,0),(.88,sign*.265,-.58),(-.9,sign*.265,-.58)]
 wing=mesh('THK_Wing_'+side,v,[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],red); wing.parent=hinge
 # window overlay on panel
 win=mesh('THK_DoorGlass_'+side,[(-.70,sign*.065,-.06),(.58,sign*.065,-.06),(.62,sign*.18,-.32),(-.73,sign*.18,-.32)],[(0,1,2,3)],dark); win.parent=hinge
 for frame,ang in [(1,0),(25,0),(97,sign*75),(121,sign*75),(193,0)]:
  hinge.rotation_euler.x=radians(ang); hinge.keyframe_insert(data_path='rotation_euler',frame=frame)
for x,ax in [(1.39,'F'),(-1.43,'R')]:
 for sign,side in [(1,'L'),(-1,'R')]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.33,depth=.22,location=(x,sign*.88,.34),rotation=(radians(90),0,0)); o=bpy.context.object; o.name='THK_Wheel_'+ax+side; o.data.materials.append(rubber); o.parent=root
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.19,depth=.225,location=(x,sign*.89,.34),rotation=(radians(90),0,0)); o=bpy.context.object; o.name='THK_Hub_'+ax+side; o.data.materials.append(metal); o.parent=root
spoiler=cube('THK_RearStabilizer',(-2.05,0,.94),(.19,1.55,.08),red); spoiler.parent=root
for name,loc,dim,ma in [('THK_FrontBumper',(2.3,0,.43),(.09,1.45,.11),rubber),('THK_RearBumper',(-2.32,0,.45),(.09,1.5,.11),rubber),('THK_Headlights',(2.31,0,.58),(.035,1.08,.08),lamp),('THK_Taillights',(-2.34,0,.67),(.035,1.15,.08),dark)]:
 o=cube(name,loc,dim,ma); o.parent=root
for name,loc in [('SOCKET_DriverSeat',(-.1,.32,.8)),('SOCKET_Muzzle_L',(1.9,.6,.65)),('SOCKET_Muzzle_R',(1.9,-.6,.65)),('SOCKET_CameraCockpit',(.25,0,1.18)),('SOCKET_Exhaust',(-2.25,0,.5)),('SOCKET_VFX_Transform',(0,0,.8))]:
 o=empty(name,loc); o.parent=root
for fr,name in [(1,'THK_RoadIdle'),(25,'THK_RoadToFlight'),(97,'THK_FlightIdle'),(121,'THK_FlightToRoad'),(193,'THK_RoadIdle_End')]: s.timeline_markers.new(name,frame=fr)
# studio
world=bpy.data.worlds.new('Studio') if not bpy.data.worlds else bpy.data.worlds[0]; s.world=world; world.color=(.22,.22,.22)
def point(obj,p): obj.rotation_euler=(Vector(p)-obj.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Key',(4,-5,7),1100,5),('Fill',(-4,4,5),900,5),('Rim',(-4,-2,5),650,3)]:
 data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; ob=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob); ob.location=loc; point(ob,(0,0,.6))
camdata=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',camdata); bpy.context.collection.objects.link(cam); s.camera=cam
s.render.engine='CYCLES'; s.cycles.samples=24; s.render.resolution_x=1000; s.render.resolution_y=700; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.frame_set(1)
views={'front':((8,0,.75),(0,0,.75)), 'rear':((-8,0,.75),(0,0,.75)), 'side':((0,-8,.8),(0,0,.8)), 'top':((0,0,8),(0,0,0)), 'perspective':((6,-7,4),(0,0,.65))}
for name,(pos,target) in views.items():
 cam.location=pos; point(cam,target); camdata.type='PERSP' if name=='perspective' else 'ORTHO'; camdata.ortho_scale=5.6; camdata.lens=45; s.render.filepath=os.path.join(ROOT,'renders',name+'.png'); bpy.ops.render.render(write_still=True)
# also expose flight state for inspection
s.frame_set(97); cam.location=(6,-7,4); point(cam,(0,0,.65)); camdata.type='PERSP'; s.render.filepath=os.path.join(ROOT,'renders','flight.png'); bpy.ops.render.render(write_still=True)
s.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Thunderhawk_Master.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.name.startswith(('THK_','SOCKET_')): o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'exports','THK_V0.fbx'),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='-Y',axis_up='Z',bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,add_leaf_bones=False)



