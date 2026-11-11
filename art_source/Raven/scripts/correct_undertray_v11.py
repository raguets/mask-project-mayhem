import bpy
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');A=P/'art_source/Raven';S=bpy.context.scene
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
assert not (A/'Raven_V11_Assembly.blend').exists()
exec(compile((P/'art_source/Hurricane/scripts/geometry.py').read_text(encoding='utf-8'),'<geometry>','exec'))
S.frame_set(1);root=bpy.data.objects['Raven_Control'];root['hover_height']=0.;bpy.context.view_layer.update()
old=bpy.data.objects['RV_FrontUndertray'];bpy.data.objects.remove(old,do_unlink=True)
CURRENT=bpy.data.collections['RV_Body'];PARENT=None;GROUP='front_assembly';clip=bpy.data.objects['RV_CompleteFront_LongitudinalPivot'];material=bpy.data.materials['RV_BlackRubberTrim']
vv=[];ff=[]
# Real pockets reserve the entire front-wheel fold, including its tire volume.
for center,size in [((.6175,0,.205),(.405,1.50,.075)),((1.22,0,.205),(.80,.20,.075)),((1.8925,0,.205),(.545,1.50,.075))]:
    x,y,z=center;dx,dy,dz=[v/2 for v in size];off=len(vv);vv += [(x+a,y+b,z+c) for a in [-dx,dx] for b in [-dy,dy] for c in [-dz,dz]];ff += [tuple(off+i for i in face) for face in [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]]
tray=mesh('RV_FrontUndertray',vv,ff,material,root=clip,bevel=.004);tray['mechanism_estimate']='Structural center spine plus fore/aft panels; wheel-fold pockets retained rather than intersecting tires.'
for y in [-.52,-.26,.26,.52]:
    ob=bpy.data.objects['RV_FrontUndersideRib_'+str(y)];bpy.data.objects.remove(ob,do_unlink=True)
    for title,a,b in [('Aft',.50,.80),('Fore',1.64,2.06)]:box('RV_FrontUndersideRib_'+str(y)+'_'+title,((a+b)/2,y,.157),(b-a,.022,.018),material,.004,root=clip)
S.frame_set(1);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(A/'Raven_V11_Assembly.blend'),compress=True)
print('FRONT_WHEEL_FOLD_POCKETS_V11_SAVED')
