from pathlib import Path
P=Path('G:/DEV/mask-project-mayhem')
code=(P/'art_source/Condor/scripts/review_v4.py').read_text().replace('v4_review','v8_review')
code=code.replace("exec(compile(code,'<v4review>','exec'))","code=code.replace('[0,-6,1.8]','[-.3,-7,1.8]').replace('[0,0,.85]','[-.2,0,.85]').replace(\"'lens':65\",\"'lens':58\")\nexec(compile(code,'<v8review>','exec'))")
exec(compile(code,'<v8review_wrapper>','exec'))
