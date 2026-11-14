from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
code=(P/'Tools/Art/import_miles_motion.py').read_text(encoding='utf-8-sig').replace('Miles','Vanessa').replace('Switchblade','Manta').replace('switchblade','manta').replace('miles','vanessa')
exec(compile(code,'<vanessa-motion-import>','exec'))
