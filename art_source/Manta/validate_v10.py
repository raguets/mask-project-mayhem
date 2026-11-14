from pathlib import Path
p=Path('G:/DEV/mask-project-mayhem/art_source/Manta/validate_v4.py').read_text().replace('validation_v4.json','validation_v10.json').replace("'version':4","'version':10")
extra=['MA_FixedHoodRearQuarter','MA_TripleLauncherCassette']+['MA_MissileRedTip'+('.%03d'%i if i else '') for i in range(3)]
# Use actual missile names resolved by the running scene rather than assuming suffix history.
import bpy
extra=['MA_FixedHoodRearQuarter','MA_TripleLauncherCassette']+[o.name for o in bpy.data.objects if o.name.startswith(('MA_PersistentMissile','MA_MissileRedTip','MA_RearWheelWingBridge','MA_RearWheelBearing','MA_RearWheelCarrierGusset','MA_MainWingForwardCannon'))]
p=p.replace("pairs=[", "names+="+repr(extra)+"\npairs=[('MA_ReactorCassette','MA_RearLightPanel')]+[")
needle="hits={a+' / '+b:[] for a,b in pairs}"
add="pairs += [('MA_SlidingHoodSkin',n) for n in "+repr(extra[1:8])+"]\npairs += [('MA_Underbody',n) for n in "+repr([n for n in extra if n.startswith('MA_MainWingForwardCannon')])+"]\n"
p=p.replace(needle,add+needle)
exec(compile(p,'<validation_v10>','exec'))
