"""Cache fixed geometry; inspect deployment surfaces through 81 sampled phases."""
import bpy,ast,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path('G:/DEV/mask-project-mayhem');S=bpy.context.scene;R=bpy.data.objects['BoulderHill_Control']
assert not bpy.app.driver_namespace.get('_mask_asset_review_active')
tree=ast.parse((P/'art_source/Boulder_Hill/scripts/validate_geometry_v1.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<functions>','exec'))
fr=S.frame_current;action=R.animation_data.action;R.animation_data.action=None;keys=['battle_mode','gate_open','thunderhawk_exit','rhino_exit'];values={k:R[k] for k in keys};report={'phase_count':81,'method':'BVH surface intersections of evaluated meshes, sampled at battle_mode increments 0.0125. Floors, own rigid assembly joins and designed rim contact excluded; no continuous or dynamics guarantee.','groups':{}}
try:
    state(battle_mode=0,gate_open=0,thunderhawk_exit=0,rhino_exit=0)
    groups=[('garage_shell',{'shop_static','rock_static','hangar_static'}),('store_armor',{'shop_static','pump_static'}),('cap',{'rock_static','turret','garage_shell'}),('turret',{'rock_static'}),('pump_gun_1',{'pump_static'}),('pump_gun_2',{'pump_static'}),('sign_panel',{'sign_guns'})]
    for moving,fixed in groups:
        static=[o for o in S.objects if o.get('BH_group') in fixed and o.get('BH_group') not in {'turret','garage_shell','sign_guns'} and not o.name.startswith(('BH_HangarFloor','BH_ShopFloor','BH_PumpFoot'))]
        ta,va,fa,na=combine(static) if static else (None,None,None,None);contacts=[];minz=[]
        for i in range(81):
            state(battle_mode=i/80)
            mov=[o for o in S.objects if o.get('BH_group')==moving];tb,vb,fb,nb=combine(mov);pairs=[]
            if ta:pairs.extend((na[a],nb[b]) for a,b in ta.overlap(tb))
            dynamic=[o for o in S.objects if o.get('BH_group') in fixed and o.get('BH_group') in {'turret','garage_shell','sign_guns'}]
            if dynamic:
                td,vd,fd,nd=combine(dynamic);pairs.extend((nd[a],nb[b]) for a,b in td.overlap(tb))
            pairs=sorted(set(pairs))
            if pairs:contacts.append({'mode':i/80,'pairs':pairs})
            if moving=='store_armor':minz.append(min(v.z for v in vb))
        report['groups'][moving]={'contacts':contacts}
        if minz:report['groups'][moving]['lowest_sampled_surface_z_m']=min(minz)
    report['invalid_drivers']=[o.name+':'+f.data_path for o in S.objects if o.animation_data for f in o.animation_data.drivers if not f.driver.is_valid]
    (P/'docs/qa/boulder_phases_final.json').write_text(json.dumps(report,indent=2))
    print('PHASES_FINAL',{k:len(v['contacts']) for k,v in report['groups'].items()},'INVALID',report['invalid_drivers'])
finally:
    for k,v in values.items():R[k]=v
    R.animation_data.action=action;S.frame_set(fr);R.update_tag();bpy.context.view_layer.update()
