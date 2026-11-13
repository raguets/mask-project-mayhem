from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
code=(P/'Tools/Art/import_onfoot_motion.py').read_text(encoding='utf-8-sig')
a=code.index('profiles=');b=code.index('\ntry:',a)
code=code[:a]+"profiles=[('Miles','Switchblade/SK_Miles','Switchblade/DA_Switchblade')]"+code[b:]
code=code.replace("REPORT=ROOT/'Saved/Art/onfoot/import.json'", "REPORT=ROOT/'Saved/Art/switchblade-locomotion-import.json'")
exec(compile(code,'<miles-motion-import>','exec'))
