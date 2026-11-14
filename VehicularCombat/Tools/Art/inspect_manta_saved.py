from pathlib import Path
import unreal
P=Path(unreal.Paths.project_dir()).resolve()
exec(compile((P/'Tools/Art/finalize_manta.py').read_text(),'<manta-readback>','exec'))
