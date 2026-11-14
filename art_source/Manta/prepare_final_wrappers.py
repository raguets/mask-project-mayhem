from pathlib import Path
P=Path(__file__).resolve().parents[2];A=P/'art_source/Manta';T=P/'VehicularCombat/Tools/Art'
for f in ['prepare_manta_game.py','author_vanessa_motion.py']:
 p=T/f;c=p.read_text();c=c.replace("('V7','V23')","('V7','V24')").replace("replace('V16','V23')","replace('V16','V24')").replace('Manta_V23_Assembly','Manta_V24_Assembly');p.write_text(c)
for f in ['export_reopen','validate_full','semantic_qa']:
 c=(A/(f+'_v23.py')).read_text().replace('V23','V24').replace('v23','v24')
 (A/(f+'_v24.py')).write_text(c)
c=(A/'review_character_v23.py').read_text().replace('v23_character','v24_character');(A/'review_character_v24.py').write_text(c)
