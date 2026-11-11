from pathlib import Path
A=Path('G:/DEV/mask-project-mayhem/art_source/Raven')
code=(A/'scripts/verify_exports_v5.py').read_text(encoding='utf-8').replace('V5','V14').replace('_v5','_v14')
code=code.replace('CalhounBurns_V1.blend','CalhounBurns_V2.blend').replace('RV_ReactorCover_VerticalSlide','RV_ReactorBlock_VerticalSlide').replace('-.32','-.197').replace('travel_032m','travel_0197m')
exec(compile(code,'<verify-exports-v14>','exec'))
