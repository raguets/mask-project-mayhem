import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(),'<geometry>','exec'))
root=bpy.data.objects['Manta_Control'];R=bpy.data.objects['VanessaWarfield_Rig'];S.frame_set(1)
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=root
purple=bpy.data.objects['MA_MainBody'].data.materials[0];metal=bpy.data.objects['MA_MainWing_1'].data.materials[0];black=bpy.data.objects['MA_Underbody'].data.materials[0]
# Preserve the aft quarter of the central hood as a fixed piece.
moving=bpy.data.objects['MA_SlidingHoodSkin'];fixed=bpy.data.objects.new('MA_FixedHoodRearQuarter',moving.data.copy());CURRENT.objects.link(fixed);fixed.parent=root
def clip(ob,x,keep_front):
 bm=bmesh.new();bm.from_mesh(ob.data);result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=(x,0,0),plane_no=(1,0,0),clear_inner=keep_front,clear_outer=not keep_front)
 edges=[e for e in bm.edges if e.is_boundary and all(abs(v.co.x-x)<.0001 for v in e.verts)]
 if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
clip(fixed,1.073,False);clip(moving,1.085,True)
fixed.modifiers.new('RoundedManufacturedEdges','BEVEL').width=.004
# Lower the nose and flat hammerhead while keeping the headlights/cannons fixed.
def drop(p):
 t=max(0,min(1,(p.x-1.45)/.67));t=t*t*(3-2*t);return .135*t
for name in ['MA_SlidingHoodSkin','MA_FixedHoodShoulder_L','MA_FixedHoodShoulder_R']:
 for v in bpy.data.objects[name].data.vertices:v.co.z-=drop(v.co)
for ob in bpy.data.objects:
 if ob.type=='MESH' and ob.name.startswith('MA_FixedHoodWellWall'):
  for v in ob.data.vertices:
   if v.co.z>.50:v.co.z-=drop(v.co)
body=bpy.data.objects['MA_MainBody']
for v in body.data.vertices:
 if v.co.x>1.45 and v.co.z>.43:v.co.z-=drop(v.co)*max(0,min(1,(v.co.z-.43)/.18))
# Reposition and shorten the persistent triple-missile assembly into the revealed bay.
launcher=bpy.data.objects['MA_TripleLauncherLift']
for ob in launcher.children:
 if ob.type!='MESH':continue
 for v in ob.data.vertices:
  v.co.x=1.26+(v.co.x-.88)*.72
  if ob.name.startswith(('MA_PersistentMissile','MA_MissileRedTip')):v.co.x=1.145+(v.co.x-1.145)*.80
drive(launcher,'location',2,'.03*t+.24*min(1,max(0,(t-.86)/.14))**2*(3-2*min(1,max(0,(t-.86)/.14)))',[('t',root,'transform')])
launcher['clearance_note']='Starts moving with all mechanisms but remains below hood until t=.86; larger lift only after whole cassette clears rear edge. Reverse retracts before panel closes.'
root['hood_note']='Fixed aft quarter X[.74,1.073]; central moving strip X[1.085,2.12] at rest, leaves missile opening behind it. Lower, 27mm-thick flat hammerhead below front cannon axes; cannons independently root-mounted.'
# Slightly broader front-wheel winglets.
for s in [-1,1]:
 ob=bpy.data.objects['MA_FrontGunWing_'+str(s)]
 for v in ob.data.vertices:v.co.y=s*(.66+(s*v.co.y-.66)*1.20)
# Small main-wing weapons belong inboard of the tips and point forward in airplane mode.
for ob in list(bpy.data.objects):
 if ob.name.startswith('MA_WingTipGun'):bpy.data.objects.remove(ob,do_unlink=True)
for s in [-1,1]:
 wing=bpy.data.objects['MA_UnderbodyWingPivot_'+str(s)]
 tube('MA_MainWingForwardCannon_'+str(s),(.15,s*.67,.09),(.15,s*.41,.09),.020,metal,root=wing)
 tube('MA_MainWingCannonBore_'+str(s),(.15,s*.409,.09),(.15,s*.404,.09),.013,black,root=wing)
 # Enlarged one-piece bearing carrier, plus triangular gusset down to the wing.
 box('MA_RearWheelWingBridge_'+str(s),(-1.41,s*.80,.29),(.34,.135,.14),metal,.025,wing)
 tube('MA_RearWheelBearing_'+str(s),(-1.24,s*.69,.32),(-1.24,s*.85,.32),.103,metal,N=48,root=wing)
 vv=[(x,s*y,z) for y in [.72,.81] for x,z in [(-1.52,.125),(-1.20,.125),(-1.20,.34),(-1.42,.37)]]
 mesh('MA_RearWheelCarrierGusset_'+str(s),vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],metal,wing,bevel=.013)
 wing['weapon_note']='Cannon at intermediate span; stored axis inward Y becomes +X forward in airplane mode. Enlarged bearing bridge rotates with the same persistent rear wheel.'
R['driving_pose']=1.;R['in_vehicle']=1.;R['mask_on']=False;R.update_tag();S.frame_set(61);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V10_Assembly.blend'),compress=True)
print('V10_SAVED')
