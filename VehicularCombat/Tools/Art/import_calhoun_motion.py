from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
code=(P/'Tools/Art/import_onfoot_motion.py').read_text(encoding='utf-8-sig')
a=code.index('profiles=');b=code.index('\ntry:',a)
code=code[:a]+"profiles=[('Calhoun','Raven/SK_Calhoun','Raven/DA_Raven')]"+code[b:]
code=code.replace("REPORT=ROOT/'Saved/Art/onfoot/import.json'", "REPORT=ROOT/'Saved/Art/raven-locomotion-import.json'")
exec(compile(code,'<calhoun-motion-import>','exec'))
