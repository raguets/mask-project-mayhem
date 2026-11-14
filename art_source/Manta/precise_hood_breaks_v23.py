import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Manta';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
exec(compile((A/'rebuild_bindings_v15.py').read_text().split('# Front tires')[0],'<helpers>','exec'))
CURRENT=bpy.data.collections['Manta_Vehicle'];PARENT=None
def basehood(x,y):
 u=max(0,min(1,(x-.73)/1.62));return .875-.025*u-.305*u*u-.005*u**5-.035*(y/.70)**2
def width(x):
 u=max(0,min(1,(x-.73)/1.62));return .33 if u<.86 else .33+.21*min(1,(u-.86)/.10)
# Include the two exact flare breakpoints in the fixed shoulder topology. Uniform
# sampling alone cut the inside corner and let it intrude into the moving flare.
piece='# Inner shoulder edge'+(A/'close_seams_frames_v22.py').read_text().split('# Inner shoulder edge')[1].split('# Rear root edge')[0]
piece=piece.replace('xs=seq(64,.73,2.35)','xs=sorted(set(seq(64,.73,2.35)+[.73+1.62*.86,.73+1.62*.96]))')
for o in list(bpy.data.objects):
 if o.name.startswith('MA_FixedHeadlightBrow'):bpy.data.objects.remove(o,do_unlink=True)
exec(compile(piece,'<exact_flare_topology>','exec'))
# Trim beads belong OUTSIDE the .340m wheel aperture, not 5mm inside it.
D=__import__('json').loads((A/'proportions_v19.json').read_text());centres=[D['front_axle_x'],D['rear_axle_x']]
for o in bpy.data.objects:
 if o.type=='CURVE' and o.name.startswith('MA_CircularArchLip'):
  for sp in o.data.splines:
   for v in sp.points:
    cx=min(centres,key=lambda x:abs(v.co.x-x));dx=v.co.x-cx;dz=v.co.z-.34;length=math.hypot(dx,dz)
    v.co.x=cx+dx*.349/length;v.co.z=.34+dz*.349/length
  o.update_tag()
for o in bpy.data.objects:
 if o.type=='MESH':o.data.update()
 o.update_tag()
S.frame_set(121);S.frame_set(1);bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(A/'Manta_V23_Assembly.blend'),compress=True)
print('V23_EXACT_FLARE_AND_OUTSIDE_ARCH_TRIM_SAVED')
