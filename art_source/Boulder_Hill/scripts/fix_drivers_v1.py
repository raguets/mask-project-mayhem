import bpy,json,math
from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem');R=bpy.data.objects['BoulderHill_Control'];S=bpy.context.scene
print('BEFORE',[(o.name,f.data_path,len(f.driver.expression),f.driver.expression) for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid])
def driver(ob,path,index,expression,names):
    f=ob.driver_add(path,index) if index is not None else ob.driver_add(path)
    d=f.driver;d.type='SCRIPTED'
    while d.variables:d.variables.remove(d.variables[0])
    for name,key in names:
        v=d.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=R;v.targets[0].data_path='["'+key+'"]'
    d.expression=expression
def prop(name,expr,names):
    R[name]=0.;driver(R,'["'+name+'"]',None,expr,names)
prop('_travel','max(min(1,max(0,t*100))*min(1,max(0,(1-t)*100)),min(1,max(0,r*100))*min(1,max(0,(1-r)*100)))',[('t','thunderhawk_exit'),('r','rhino_exit')])
prop('_garage','max(d,min(1,max(0,b/.32)),t)',[('d','garage_deploy'),('b','battle_mode'),('t','_travel')])
prop('_gate','min(max(g,t),min(1,max(0,(d-.98)/.02)))',[('g','gate_open'),('t','_travel'),('d','_garage')])
for i,sg in [(1,-1),(2,1)]:driver(bpy.data.objects['BH_ExitGateHinge_'+str(i)],'rotation_euler',2,str(sg*1.78)+'*g',[('g','_gate')])
prop('_cap','max(v,min(1,max(0,(b-.57)/.22)))',[('v','boulder_fall'),('b','battle_mode')])
for index,values in [(0,(7,10,23,22)),(1,(6,6,1,1)),(2,(13.22,17.3,8,.85))]:
    a,b,c,d=values
    driver(bpy.data.objects['BH_FallingBoulder'],'location',index,f'{a}*(1-t)**3+{3*b}*(1-t)**2*t+{3*c}*(1-t)*t*t+{d}*t**3',[('t','_cap')])
for o in S.objects:
    if o.name.startswith('BH_HangarRoofBeam_'):o.location.z+=.25
for o in S.objects:
    if o.animation_data:
        for f in o.animation_data.drivers:f.driver.expression+=' + 0.0'
    o.update_tag()
S.frame_set(181);bpy.context.view_layer.update();S.frame_set(1);bpy.context.view_layer.update()
bad=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
print('AFTER',bad)
assert not bad
bpy.ops.wm.save_as_mainfile(filepath=str(P/'art_source/Boulder_Hill/BoulderHill_V1_Assembly.blend'),compress=True)
