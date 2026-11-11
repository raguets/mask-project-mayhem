import os
from pathlib import Path
os.environ['THK13_VIEWS']='face,face_profile,spectrum,spectrum_profile,standing,glass'
exec(compile(Path('G:/DEV/mask-project-mayhem/art_source/Thunderhawk/scripts/review_thunderhawk_v13.py').read_text(),'review_thunderhawk_v13.py','exec'))
os.environ.pop('THK13_VIEWS',None)
